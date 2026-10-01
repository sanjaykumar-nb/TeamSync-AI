import json
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "TeamSync AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    # Off unless asked for: it opens /docs and /redoc. docker-compose.yml turns it
    # on for local work; the production override leaves it off.
    DEBUG: bool = False
    # Log every SQL statement. Useful when debugging a query, and slow: it was on
    # whenever DEBUG was (the default) until the load test showed the cost.
    SQL_ECHO: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://teamsync:teamsync_dev_password@localhost:5432/teamsync"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # How many sign-in or sign-up attempts one caller may make per window. 0 turns it off.
    AUTH_RATE_LIMIT_ATTEMPTS: int = 10
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = 60
    # Only true when a reverse proxy really is in front: it makes the app believe
    # X-Forwarded-For, which any caller can otherwise set to anything.
    TRUST_PROXY_HEADERS: bool = False

    # JWT
    JWT_SECRET: str = "your-super-secret-key-min-32-characters-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # GitHub (optional): a read-only token raises the API rate limit and reaches private repos.
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_API_URL: str = "https://api.github.com"

    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8001"
    GROQ_API_KEY: Optional[str] = None

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@teamsync.ai"

    # CORS — the sites a browser may call this API from. Written as a plain list
    # ("https://a.example,https://b.example") or as JSON; read through cors_origins.
    # It was a list[str], which meant a non-JSON value stopped the app at startup.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []
        if raw.startswith("["):
            return [str(origin).rstrip("/") for origin in json.loads(raw)]
        return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()