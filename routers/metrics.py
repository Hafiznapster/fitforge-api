# fitforge-api/routers/metrics.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
from middleware.auth import get_current_user
from database import supabase

router = APIRouter()

class BodyMetricCreate(BaseModel):
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    waist_cm: Optional[float] = None

@router.post("/water-log", status_code=status.HTTP_201_CREATED)
async def log_water(glasses: int, user_id: str = Depends(get_current_user)):
    try:
        payload = {
            "user_id": user_id,
            "glasses": glasses
        }
        res = supabase.table("water_logs").insert(payload).execute()
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log water: {str(e)}")

@router.get("/water-log")
async def get_water_log(target_date: Optional[date] = None, user_id: str = Depends(get_current_user)):
    try:
        query = supabase.table("water_logs").select("*").eq("user_id", user_id)
        if target_date:
            query = query.eq("logged_at", target_date.isoformat())

        res = query.execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch water logs: {str(e)}")

@router.post("/", status_code=status.HTTP_201_CREATED)
async def log_body_metric(metric: BodyMetricCreate, user_id: str = Depends(get_current_user)):
    try:
        payload = metric.model_dump(exclude_unset=True)
        payload['user_id'] = user_id
        res = supabase.table("body_metrics").insert(payload).execute()
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log metric: {str(e)}")

@router.get("/")
async def get_body_metrics(user_id: str = Depends(get_current_user)):
    try:
        res = supabase.table("body_metrics").select("*").eq("user_id", user_id).order("logged_at", ascending=False).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")
