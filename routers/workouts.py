# fitforge-api/routers/workouts.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date
from models.workout import WorkoutSessionCreate, WorkoutExerciseCreate, WorkoutSessionResponse, WorkoutExerciseResponse
from middleware.auth import get_current_user
from database import supabase

router = APIRouter()

@router.post("/", response_model=WorkoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(session_data: WorkoutSessionCreate, user_id: str = Depends(get_current_user)):
    try:
        # 1. Insert the workout session
        session_payload = session_data.model_dump(exclude={'exercises'})
        session_payload['user_id'] = user_id

        session_res = supabase.table("workout_sessions").insert(session_payload).execute()
        session = session_res.data[0]
        session_id = session['id']

        # 2. Insert nested exercises
        if session_data.exercises:
            exercises_payload = []
            for ex in session_data.exercises:
                ex_dict = ex.model_dump()
                ex_dict['session_id'] = session_id
                ex_dict['user_id'] = user_id
                exercises_payload.append(ex_dict)

            supabase.table("workout_exercises").insert(exercises_payload).execute()

        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workout: {str(e)}")

@router.get("/", response_model=List[WorkoutSessionResponse])
async def get_workouts(target_date: Optional[date] = None, user_id: str = Depends(get_current_user)):
    try:
        query = supabase.table("workout_sessions").select("*, workout_exercises(*)").eq("user_id", user_id)

        if target_date:
            start_date = target_date.isoformat()
            end_date = f"{target_date.isoformat()} 23:59:59"
            query = query.gte("logged_at", start_date).lte("logged_at", end_date)

        res = query.execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch workouts: {str(e)}")

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(session_id: str, user_id: str = Depends(get_current_user)):
    try:
        # Verify ownership first
        session = supabase.table("workout_sessions").select("user_id").eq("id", session_id).single().execute()
        if not session.data or session.data['user_id'] != user_id:
            raise HTTPException(status_code=404, detail="Workout session not found or access denied")

        # Delete session (exercises are deleted via cascade in schema.sql)
        supabase.table("workout_sessions").delete().eq("id", session_id).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete workout: {str(e)}")
