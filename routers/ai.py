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

    # Save to DB
    try:
        supabase.table("ai_interactions").insert({
            "user_id": user_id,
            "task_type": "chat",
            "prompt": req.message,
            "response": result['content'],
            "provider": result['provider']
        }).execute()
    except Exception as e:
        print(f"Error saving AI chat: {e}")

    return AIResponse(content=result['content'], provider=result['provider'])

@router.post('/workout-plan', response_model=AIResponse)
async def generate_workout_plan(req: PlanRequest, user_id: str = Depends(get_current_user)):
    prompt = f"Generate a detailed {req.experience_level} level {req.muscle_group} workout. Include: exercise name, sets, reps, rest time, form tips. Format as a structured list. Maximum 6 exercises."
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': prompt}
    ]
    result = await route_ai_request(messages, task='plan')

    # Save to DB
    try:
        supabase.table("ai_interactions").insert({
            "user_id": user_id,
            "task_type": "plan",
            "prompt": prompt,
            "response": result['content'],
            "provider": result['provider']
        }).execute()
    except Exception as e:
        print(f"Error saving AI plan: {e}")

    return AIResponse(content=result['content'], provider=result['provider'])

@router.post('/meal-suggestion', response_model=AIResponse)
async def meal_suggestion(req: ChatRequest, user_id: str = Depends(get_current_user)):
    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': req.message}
    ]
    result = await route_ai_request(messages, task='suggest')

    # Save to DB
    try:
        supabase.table("ai_interactions").insert({
            "user_id": user_id,
            "task_type": "suggest",
            "prompt": req.message,
            "response": result['content'],
            "provider": result['provider']
        }).execute()
    except Exception as e:
        print(f"Error saving AI suggestion: {e}")

    return AIResponse(content=result['content'], provider=result['provider'])
