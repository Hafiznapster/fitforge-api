from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = [] # Expected: [{'role': 'user'|'assistant', 'content': '...'}]

class PlanRequest(BaseModel):
    muscle_group: str
    experience_level: str # 'beginner', 'intermediate', 'advanced'

class AIResponse(BaseModel):
    content: str
    provider: str # 'groq', 'gemini', or 'openrouter'
