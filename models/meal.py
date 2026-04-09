from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class MealBase(BaseModel):
    name: str
    calories: int
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fiber_g: float = 0.0
    meal_type: str = 'snack' # 'breakfast','lunch','dinner','snack','pre','post'
    notes: Optional[str] = None
    logged_at: Optional[datetime] = None

class MealCreate(MealBase):
    pass

class MealUpdate(BaseModel):
    name: Optional[str] = None
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    meal_type: Optional[str] = None
    notes: Optional[str] = None
    logged_at: Optional[datetime] = None

class MealResponse(MealBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
