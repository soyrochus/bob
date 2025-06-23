from __future__ import annotations

"""Project configuration utilities."""

from functools import lru_cache
from pathlib import Path
from typing import Protocol, Optional, List, Dict, Any
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
        self._global: Dict = data.get("global", {})
        self._agents: Dict[str, Dict] = data.get("agents", {})

        # Global settings
        self.DATABASE_URL = self._global.get("database_url", "sqlite+aiosqlite:///./db/bob.db")
        self.HOST = self._global.get("host", "0.0.0.0")
        self.PORT = int(self._global.get("port", 8000))
        self.REDIS_URL = self._global.get("redis_url", "redis://localhost:6379/0")

        # Environment fallbacks for agent-specific keys
        self._env_openai_api_key = os.getenv("OPENAI_API_KEY")
        self._env_llm_provider = os.getenv("LLM_PROVIDER")

        self._llms: Dict[str, Any] = {}
        self._vector_dbs: Dict[str, Any] = {}

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

    def get_openai_api_key(self, name: str) -> Optional[str]:
        """Return OpenAI API key for ``name`` with environment fallback."""
        return self.get_agent_param(name, "openai_api_key", self._env_openai_api_key)

    def get_llm_provider(self, name: str) -> str:
        """Return the LLM provider configured for ``name``."""
        return self.get_agent_param(name, "llm", self._env_llm_provider or "openai")

    def get_llm(self, name: str):
        """Return a cached LLM instance for ``name``."""
        if name not in self._llms:
            from .llm import OpenAILLM  # local import to avoid circular

            provider = self.get_llm_provider(name)
            if provider == "openai":
                api_key = self.get_openai_api_key(name)
                model = self.get_agent_param(name, "openai_model", "gpt-4.1")
                self._llms[name] = OpenAILLM(api_key, model)
            else:  # pragma: no cover - unsupported provider branch
                raise ValueError(f"Unsupported LLM provider: {provider}")
        return self._llms[name]

    def get_vector_db(self, name: str):
        """Return a cached vector DB instance for ``name`` (may be ``None``)."""
        if name not in self._vector_dbs:
            try:  # optional dependency
                from langchain.embeddings import OpenAIEmbeddings
                from langchain.vectorstores import Chroma
            except Exception:  # pragma: no cover - optional deps
                OpenAIEmbeddings = None
                Chroma = None

            db = None
            db_type = self.get_agent_param(name, "vector_db_type")
            if db_type == "Chroma" and Chroma:
                path = self.get_agent_param(name, "vector_db_path", "chroma")
                embedding_type = self.get_agent_param(name, "vector_db_embedding", "openai")
                if embedding_type == "openai" and OpenAIEmbeddings:
                    embeddings = OpenAIEmbeddings(
                        openai_api_key=self.get_openai_api_key(name)
                    )
                else:  # pragma: no cover - unsupported embedding
                    embeddings = None
                db = Chroma(persist_directory=path, embedding_function=embeddings)
            self._vector_dbs[name] = db
        return self._vector_dbs[name]


@lru_cache(maxsize=1)
def get_settings(provider: Optional[SettingsProvider] = None, path: Optional[str] = None) -> Settings:
    return Settings(provider, path)


settings = get_settings()
