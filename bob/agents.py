from __future__ import annotations

"""Agent implementations and dynamic registry.

Agents are configured in ``bob-config.toml`` under ``[agents.ID]`` sections.
Each section may specify ``agent_type`` to override the class name.  If the
field is omitted, the section ID itself is used as the type name.  When present,
``home_selector`` provides the label for the frontend agent picker.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterable, Dict, List, Tuple, Type

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


# ---------------------------------------------------------------------------
# Dynamic agent registry
# ---------------------------------------------------------------------------

#: Registered agent classes keyed by ``agent_type`` name
_AGENT_TYPES: Dict[str, Type[BaseAgent]] = {}

#: Cached agent instances keyed by agent ID from the configuration
_AGENT_INSTANCES: Dict[str, BaseAgent] = {}

#: Selector options as ``(ID, label)`` tuples for the frontend
_SELECTOR_CHOICES: List[Tuple[str, str]] = []


def register_agent_type(name: str, cls: Type[BaseAgent]) -> None:
    """Register an agent class for dynamic instantiation."""

    _AGENT_TYPES[name.lower()] = cls


def _instantiate_agent(agent_id: str) -> BaseAgent:
    """Instantiate the agent configured under ``agents.agent_id``.

    ``agent_type`` may be specified in the config to override the class
    name.  If omitted, the agent ID itself is used as the type name.
    """

    agent_type = settings.get_agent_param(agent_id, "agent_type", agent_id)
    agent_type = str(agent_type).lower()
    cls = _AGENT_TYPES.get(agent_type)
    if not cls:
        raise ValueError(f"Unknown agent_type '{agent_type}' for agent '{agent_id}'")

    try:
        return cls(agent_id)  # most agents expect the id
    except TypeError:
        # fall back to parameterless constructor
        return cls()


def load_agents() -> None:
    """Parse ``[agents.*]`` sections and instantiate all agents."""

    _AGENT_INSTANCES.clear()  # ensure single instantiation per reload
    _SELECTOR_CHOICES.clear()

    for agent_id in settings.get_agent_names():
        instance = _instantiate_agent(agent_id)
        _AGENT_INSTANCES[agent_id] = instance
        label = settings.get_agent_param(agent_id, "home_selector")
        if label is not None:
            _SELECTOR_CHOICES.append((agent_id, str(label)))


def get_agent(name: str) -> BaseAgent:
    """Return a cached agent instance by ``name``."""

    if not _AGENT_INSTANCES:
        load_agents()

    try:
        return _AGENT_INSTANCES[name.lower()]
    except KeyError:  # pragma: no cover - invalid name branch
        raise ValueError(f"Unknown agent selector: {name}")


def get_selector_choices() -> List[Tuple[str, str]]:
    """Return ``(ID, label)`` tuples for agents in the frontend selector."""

    if not _AGENT_INSTANCES:
        load_agents()
    return list(_SELECTOR_CHOICES)


# Register built-in agent types and eagerly load configured agents
register_agent_type("default", DefaultAgent)
register_agent_type("bob", BobAgent)
register_agent_type("tutor", TutorAgent)

load_agents()
