from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import get_current_user
from database import supabase
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
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

@router.get('/profiles/me')
async def get_profile(user_id: str = Depends(get_current_user)):
    response = supabase.table('profiles').select('*').eq('id', user_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return response.data

@router.patch('/profiles/me')
async def update_profile(update_data: ProfileUpdate, user_id: str = Depends(get_current_user)):
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    response = supabase.table('profiles').update(update_dict).eq('id', user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")
    return response.data[0]
