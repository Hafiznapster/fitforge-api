# fitforge-api/models/workout.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class WorkoutExerciseCreate(BaseModel):
    exercise_name: str
    sets: int = 3
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_sec: Optional[int] = None
    rest_sec: int = 90
    notes: Optional[str] = None
    order_index: int = 0

class WorkoutSessionCreate(BaseModel):
    name: str
    type: str = "strength"
    duration_min: Optional[int] = None
    calories_burned: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[WorkoutExerciseCreate] = []

class WorkoutExerciseResponse(BaseModel):
    id: UUID
    exercise_name: str
    sets: int
    reps: Optional[int]
    weight_kg: Optional[float]
    duration_sec: Optional[int]
    rest_sec: int
    notes: Optional[str]
    order_index: int

class WorkoutSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    type: str
    duration_min: Optional[int]
    calories_burned: Optional[int]
    notes: Optional[str]
    logged_at: str
    workout_exercises: Optional[List[WorkoutExerciseResponse]] = None
