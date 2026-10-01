from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "TeamSync AI Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    GROQ_API_KEY: Optional[str] = None
    AI_MODEL: str = "openai/gpt-oss-120b"  # Groq deprecated the llama-3.x family; see README Troubleshooting
    AI_TEMPERATURE: float = 0.1
    AI_MAX_TOKENS: int = 4096
    AI_TIMEOUT_SECONDS: int = 60
    
    DATABASE_URL: str = "postgresql+asyncpg://teamsync:teamsync_dev_password@localhost:5432/teamsync"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # A plain list ("http://a,http://b") or JSON; read through cors_origins.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://localhost:8001"

    @property
    def cors_origins(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []
        if raw.startswith("["):
            import json

            return [str(origin).rstrip("/") for origin in json.loads(raw)]
        return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()