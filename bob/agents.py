from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterable

from . import llm
from .settings import settings

try:
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
except Exception:  # pragma: no cover - optional dependency
    OpenAIEmbeddings = None
    Chroma = None


class BaseAgent(ABC):
    """Shared interface for all agents."""

    @abstractmethod
    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterable[str]:
        """Stream response tokens for the given messages."""
        raise NotImplementedError


class DefaultAgent(BaseAgent):
    """Default agent using the raw LLM provider."""

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterable[str]:
        async for token in llm.stream_tokens(messages):
            yield token


class BobAgent(BaseAgent):
    """RAG-enabled agent using a local Chroma vector database."""

    def __init__(self) -> None:
        self._vector_db = self._init_vector_db()

    def _init_vector_db(self):  # pragma: no cover - simple configuration helper
        if not Chroma or not OpenAIEmbeddings:
            return None
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        return Chroma(persist_directory="chroma", embedding_function=embeddings)

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterable[str]:
        prompt = messages[-1]["content"] if messages else ""
        context = ""
        if self._vector_db:
            docs = self._vector_db.similarity_search(prompt, k=3)
            context = "\n".join(d.page_content for d in docs)
        composed = messages.copy()
        if context:
            composed.append({"role": "system", "content": context})
        async for token in llm.stream_tokens(composed):
            yield token


class TutorAgent(BobAgent):
    """Alias for BobAgent to be extended later."""


def get_agent(name: str) -> BaseAgent:
    """Factory returning an agent instance based on ``name``."""
    if name == "default":
        return DefaultAgent()
    if name == "Bob":
        return BobAgent()
    if name == "tutor":
        return TutorAgent()
    raise ValueError(f"Unknown agent selector: {name}")
