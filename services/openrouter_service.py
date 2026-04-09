# fitforge-api/services/openrouter_service.py
import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

async def openrouter_chat(messages: list) -> str:
    if not settings.OPENROUTER_API_KEY:
        raise RuntimeError("OpenRouter API key not configured")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Using a free model via OpenRouter
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise e
