# fitforge-api/services/gemini_service.py
import google.generativeai as genai
from config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Gemini if API key exists
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize model
model = None
if settings.GEMINI_API_KEY:
    model = genai.GenerativeModel('gemini-2.5-flash-lite')

async def gemini_chat(messages: list) -> str:
    if model is None:
        raise RuntimeError("Gemini API key not configured")

    try:
        # Convert OpenAI-style messages to Gemini format
        # Gemini expects 'user' and 'model' roles
        history = []
        for msg in messages[:-1]:  # All but last
            role = 'user' if msg['role'] == 'user' else 'model'
            history.append({'role': role, 'parts': [msg['content']]})

        chat = model.start_chat(history=history)
        # The last message is the current prompt
        response = await chat.send_message_async(messages[-1]['content'])
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise e
