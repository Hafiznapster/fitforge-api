# fitforge-api/routers/profiles.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from pydantic import BaseModel
from middleware.auth import get_current_user
from database import supabase

router = APIRouter()

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    calorie_goal: Optional[int] = None
    protein_goal: Optional[int] = None
    carb_goal: Optional[int] = None
    fat_goal: Optional[int] = None

@router.get("/me")
async def get_profile(user_id: str = Depends(get_current_user)):
    res = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return res.data

@router.patch("/me")
async def update_profile(update: ProfileUpdate, user_id: str = Depends(get_current_user)):
    # Filter out None values for partial update
    update_data = update.model_dump(exclude_unset=True)

    res = supabase.table("profiles").update(update_data).eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return res.data
