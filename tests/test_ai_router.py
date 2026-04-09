import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
from types import ModuleType

# 1. Mock Environment Variables BEFORE any imports to satisfy Pydantic Settings
os.environ["SUPABASE_URL"] = "http://mock.supabase.co"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock_key"
os.environ["GROQ_API_KEY"] = "mock_groq"
os.environ["GEMINI_API_KEY"] = "mock_gemini"
os.environ["OPENROUTER_API_KEY"] = "mock_openrouter"

# 2. Mock external AI libraries to avoid dependency installation errors
def mock_module(name, attributes=None):
    m = ModuleType(name)
    if attributes:
        for attr, val in attributes.items():
            setattr(m, attr, val)
    sys.modules[name] = m

# Mock the top-level 'google' package and the specific submodule
# Gemini service calls genai.configure(...)
mock_module('google', {})
mock_module('google.generativeai', {
    'configure': MagicMock(),
    'GenerativeModel': MagicMock()
})
mock_module('groq', {
    'AsyncGroq': MagicMock()
})

# Now import the service under test
from services.ai_router import route_ai_request, AIProvider

@pytest.mark.asyncio
async def test_route_ai_request_groq_success():
    """Test success on first attempt (Groq)."""
    with patch('services.ai_router.groq_chat', new_callable=AsyncMock) as mock_groq:
        mock_groq.return_value = "Groq response"

        messages = [{"role": "user", "content": "Hello"}]
        result = await route_ai_request(messages)

        assert result == {'content': 'Groq response', 'provider': AIProvider.GROQ}
        mock_groq.assert_called_once()

@pytest.mark.asyncio
async def test_route_ai_request_gemini_fallback():
    """Test failure of Groq, success on second attempt (Gemini)."""
    with patch('services.ai_router.groq_chat', new_callable=AsyncMock) as mock_groq, \
         patch('services.ai_router.gemini_chat', new_callable=AsyncMock) as mock_gemini:

        mock_groq.side_effect = Exception("Groq API Error")
        mock_gemini.return_value = "Gemini response"

        messages = [{"role": "user", "content": "Hello"}]
        result = await route_ai_request(messages)

        assert result == {'content': 'Gemini response', 'provider': AIProvider.GEMINI}
        mock_groq.assert_called_once()
        mock_gemini.assert_called_once()

@pytest.mark.asyncio
async def test_route_ai_request_openrouter_fallback():
    """Test failure of Groq and Gemini, success on third attempt (OpenRouter)."""
    with patch('services.ai_router.groq_chat', new_callable=AsyncMock) as mock_groq, \
         patch('services.ai_router.gemini_chat', new_callable=AsyncMock) as mock_gemini, \
         patch('services.ai_router.openrouter_chat', new_callable=AsyncMock) as mock_or:

        mock_groq.side_effect = Exception("Groq API Error")
        mock_gemini.side_effect = Exception("Gemini API Error")
        mock_or.return_value = "OpenRouter response"

        messages = [{"role": "user", "content": "Hello"}]
        result = await route_ai_request(messages)

        assert result == {'content': 'OpenRouter response', 'provider': AIProvider.OPENROUTER}
        mock_groq.assert_called_once()
        mock_gemini.assert_called_once()
        mock_or.assert_called_once()

@pytest.mark.asyncio
async def test_route_ai_request_total_failure():
    """Test total failure (all three fail) and ensuring the RuntimeError is raised."""
    with patch('services.ai_router.groq_chat', new_callable=AsyncMock) as mock_groq, \
         patch('services.ai_router.gemini_chat', new_callable=AsyncMock) as mock_gemini, \
         patch('services.ai_router.openrouter_chat', new_callable=AsyncMock) as mock_or:

        mock_groq.side_effect = Exception("Groq Error")
        mock_gemini.side_effect = Exception("Gemini Error")
        mock_or.side_effect = Exception("OpenRouter Error")

        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(RuntimeError, match="All AI providers failed"):
            await route_ai_request(messages)

        mock_groq.assert_called_once()
        mock_gemini.assert_called_once()
        mock_or.assert_called_once()
