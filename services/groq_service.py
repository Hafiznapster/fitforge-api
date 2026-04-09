# fitforge-api/services/groq_service.py
from groq import AsyncGroq
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize client only if API key exists
client = None
if settings.GROQ_API_KEY:
    client = AsyncGroq(api_key=settings.GROQ_API_KEY)

async def groq_chat(messages: list) -> str:
    if client is None:
        raise RuntimeError("Groq API key not configured")

    try:
        response = await client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=messages,
            max_tokens=800,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise e
