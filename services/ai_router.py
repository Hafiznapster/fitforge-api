# fitforge-api/services/ai_router.py
import logging
from enum import Enum
from services.groq_service import groq_chat
from services.gemini_service import gemini_chat
from services.openrouter_service import openrouter_chat

logger = logging.getLogger(__name__)

class AIProvider(str, Enum):
    GROQ = 'groq'
    GEMINI = 'gemini'
    OPENROUTER = 'openrouter'

async def route_ai_request(messages: list, task: str = 'chat') -> dict:
    """
    Route AI request through providers with automatic fallback.
    task: 'chat' | 'plan' | 'suggest'
    """
    providers = [
        (AIProvider.GROQ, groq_chat),
        (AIProvider.GEMINI, gemini_chat),
        (AIProvider.OPENROUTER, openrouter_chat),
    ]

    for provider, fn in providers:
        try:
            response = await fn(messages)
            logger.info(f'AI response successfully received from {provider}')
            return {'content': response, 'provider': provider}
        except Exception as e:
            logger.warning(f'{provider} failed: {e}, trying next provider...')
            continue

    raise RuntimeError('All AI providers failed. Check API keys and quotas.')
