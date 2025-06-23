from __future__ import annotations

"""Project configuration utilities."""

from functools import lru_cache
from pathlib import Path
from typing import Protocol, Optional, List, Dict
import os
import tomllib


class SettingsProvider(Protocol):
    """Protocol for loading configuration data."""

    def load(self, path: str) -> Dict:
        """Load a configuration file and return a dictionary."""
        ...


class TomlSettingsProvider:
    """Load settings from a TOML file."""

    def load(self, path: str) -> Dict:
        with open(path, "rb") as fh:
            return tomllib.load(fh)


class Settings:
    """Application settings with pluggable configuration provider.

    Usage example::

        settings = Settings()
        print(settings.get_agent_names())
    """

    def __init__(self, provider: Optional[SettingsProvider] = None, path: Optional[str] = None) -> None:
        self._provider = provider or TomlSettingsProvider()
        self._path = self._discover_path(path)
        data: Dict = {}
        if self._path:
            try:
                data = self._provider.load(self._path)
            except Exception:
                data = {}
        self._agents: Dict[str, Dict] = data.get("agents", {})

        # Legacy environment settings
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./db/bob.db")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 8000))
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or self.get_agent_param("default", "openai_api_key")
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", self.get_agent_param("default", "llm", "openai"))

    def _discover_path(self, path: Optional[str]) -> Optional[str]:
        candidates: List[Path] = []
        if path:
            candidates.append(Path(path))
        env = os.getenv("bob_config_path")
        if env:
            candidates.append(Path(env))
        if not candidates:
            for name in ("bob-config.toml", "bobconfig.toml", "bob.toml"):
                candidates.append(Path.cwd() / name)
        for p in candidates:
            if p.is_file():
                return str(p)
        return None

    def get_agent_names(self) -> List[str]:
        return list(self._agents.keys())

    def get_agent(self, name: str) -> Dict:
        return self._agents.get(name, {})

    def get_agent_param(self, name: str, param: str, default=None):
        return self.get_agent(name).get(param, default)


@lru_cache(maxsize=1)
def get_settings(provider: Optional[SettingsProvider] = None, path: Optional[str] = None) -> Settings:
    return Settings(provider, path)


settings = get_settings()
