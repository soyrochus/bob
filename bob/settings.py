from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./db/bob.db"
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LLM_PROVIDER: str = "openai"
    REDIS_URL: str = "redis://localhost:6379/0"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
