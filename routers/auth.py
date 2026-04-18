from fastapi import APIRouter, Depends, HTTPException
from middleware.auth import get_current_user
from database import supabase
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
