# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str
    OPENAI_API_KEY: str | None
    OPENAI_MODEL: str
    HOST: str
    PORT: int
    LLM_PROVIDER: str
    REDIS_URL: str

    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./db/bob.db")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 8000))
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
