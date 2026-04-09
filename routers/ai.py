from fastapi import APIRouter, Depends, HTTPException
from models.ai import ChatRequest, PlanRequest, AIResponse
from services.ai_router import route_ai_request
from middleware.auth import get_current_user

router = APIRouter()

SYSTEM_PROMPT = '''You are FitForge AI, a knowledgeable fitness and nutrition assistant.
You help users with workout planning, diet advice, calorie guidance, and motivation.
Keep responses concise and actionable. Always emphasise safety.
Do not provide medical diagnoses. Suggest consulting a doctor for medical concerns.'''

@router.post('/chat', response_model=AIResponse)
async def chat(req: ChatRequest, user_id: str = Depends(get_current_user)):
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        *req.history,
        {'role': 'user', 'content': req.message}
    ]
    result = await route_ai_request(messages, task='chat')
    return AIResponse(content=result['content'], provider=result['provider'])

@router.post('/workout-plan', response_model=AIResponse)
async def generate_workout_plan(req: PlanRequest, user_id: str = Depends(get_current_user)):
    prompt = f"Generate a detailed {req.experience_level} level {req.muscle_group} workout. Include: exercise name, sets, reps, rest time, form tips. Format as a structured list. Maximum 6 exercises."
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': prompt}
    ]
    result = await route_ai_request(messages, task='plan')
    return AIResponse(content=result['content'], provider=result['provider'])

@router.post('/meal-suggestion', response_model=AIResponse)
async def meal_suggestion(req: ChatRequest, user_id: str = Depends(get_current_user)):
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': req.message}
    ]
    result = await route_ai_request(messages, task='suggest')
    return AIResponse(content=result['content'], provider=result['provider'])

from services.together_service import scan_food_image
from pydantic import BaseModel

class ScanFoodRequest(BaseModel):
    image_base64: str

@router.post('/scan-food')
async def scan_food(req: ScanFoodRequest, user_id: str = Depends(get_current_user)):
    result = await scan_food_image(req.image_base64)
    return result
