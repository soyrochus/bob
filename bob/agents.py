from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterable

from . import llm
from .settings import settings


class BaseAgent(ABC):
    """Shared interface for all agents."""

    @abstractmethod
    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterable[str]:
        """Stream response tokens for the given messages."""
        raise NotImplementedError


class DefaultAgent(BaseAgent):
    """Default agent using the raw LLM provider."""

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterable[str]:
        async for token in llm.stream_tokens(messages, "default"):
            yield token


class BobAgent(BaseAgent):
    """RAG-enabled agent using a local Chroma vector database."""

    def __init__(self, agent_name: str) -> None:
        self._agent_name = agent_name
        self._vector_db = settings.get_vector_db(agent_name)

    async def stream(self, messages: list[dict[str, str]]) -> AsyncIterable[str]:
        prompt = messages[-1]["content"] if messages else ""
        context = ""
        if self._vector_db:
            docs = self._vector_db.similarity_search(prompt, k=3)
            context = "\n".join(d.page_content for d in docs)
            #print(f"Context retrieved: {context}")
        composed = messages.copy()
        if context:
            composed.append({"role": "system", "content": context})
        async for token in llm.stream_tokens(composed, self._agent_name):
            yield token


class TutorAgent(BobAgent):
    """Alias for BobAgent to be extended later."""

    def __init__(self, agent_name: str) -> None:
        super().__init__(agent_name)


def get_agent(name: str) -> BaseAgent:

    name = name.lower()
    """Factory returning an agent instance based on ``name``."""
    if name == "default":
        return DefaultAgent()
    if name == "bob":
        return BobAgent("bob")
    if name == "tutor":
        return TutorAgent("tutor")
    raise ValueError(f"Unknown agent selector: {name}")
