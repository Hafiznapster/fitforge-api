from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8081", "http://localhost:8082", "https://fitforge-api-pahz.onrender.com", "https://fitforge-app.vercel.app"]

    model_config = {
        "env_file": ".env"
    }

settings = Settings()
