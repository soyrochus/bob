from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterable

import openai

from .settings import settings


class BaseLLM(ABC):
    """Abstract LLM interface."""

    @abstractmethod
    async def generate_text(self, messages: list[dict]) -> str:
        pass

    @abstractmethod
    async def stream_tokens(self, messages: list[dict]) -> AsyncIterable[str]:
        pass


class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str, model: str) -> None:
        openai.api_key = api_key
        self.model = model

    async def generate_text(self, messages: list[dict]) -> str:
        response = await openai.ChatCompletion.acreate(model=self.model, messages=messages)
        return response.choices[0].message["content"]

    async def stream_tokens(self, messages: list[dict]) -> AsyncIterable[str]:
        response = await openai.ChatCompletion.acreate(model=self.model, messages=messages, stream=True)
        async for chunk in response:
            delta = chunk.choices[0]["delta"].get("content")
            if delta:
                yield delta


_provider: BaseLLM
if settings.LLM_PROVIDER == "openai":
    _provider = OpenAILLM(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
else:
    raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")


async def generate_text(messages: list[dict]) -> str:
    return await _provider.generate_text(messages)


async def stream_tokens(messages: list[dict]) -> AsyncIterable[str]:
    async for token in _provider.stream_tokens(messages):
        yield token
