# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

"""Interfaces to language model providers."""

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




async def generate_text(messages: list[dict], agent_name: str = "default") -> str:
    """Return the full response text from the configured LLM."""
    provider = settings.get_llm(agent_name)
    return await provider.generate_text(messages)


async def stream_tokens(messages: list[dict], agent_name: str = "default") -> AsyncIterable[str]:
    """Yield response tokens from the configured LLM."""
    provider = settings.get_llm(agent_name)
    async for token in provider.stream_tokens(messages):
        yield token
