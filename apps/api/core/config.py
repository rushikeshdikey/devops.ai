from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/devops"
    JWT_SECRET: str = "replace-me-with-secure-secret-key-min-32-chars"
    ACCESS_TOKEN_TTL_MIN: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 7
    CORS_ORIGIN: str = "http://localhost:5173"
    LOG_LEVEL: str = "info"
    RATE_LIMIT_REDIS_URL: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
