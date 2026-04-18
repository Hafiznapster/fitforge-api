from fastapi import APIRouter, Depends, HTTPException, Query, status
from middleware.auth import get_current_user
from database import supabase
from models.meal import MealCreate, MealResponse
from typing import List, Optional
from datetime import date

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_meal(meal: MealCreate, user_id: str = Depends(get_current_user)):
    try:
        meal_data = meal.model_dump()
        meal_data['user_id'] = user_id
        res = supabase.table("meals").insert(meal_data).execute()
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def get_meals(target_date: Optional[date] = None, user_id: str = Depends(get_current_user)):
    try:
        query = supabase.table("meals").select("*").eq("user_id", user_id)
        if target_date:
            start_date = target_date.isoformat()
            end_date = f"{target_date.isoformat()} 23:59:59"
            query = query.gte("logged_at", start_date).lte("logged_at", end_date)

        res = query.execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal(meal_id: str, user_id: str = Depends(get_current_user)):
    res = supabase.table("meals").select("user_id").eq("id", meal_id).single().execute()
    if not res.data or res.data['user_id'] != user_id:
        raise HTTPException(status_code=404, detail="Meal not found")

    supabase.table("meals").delete().eq("id", meal_id).execute()
    return None
