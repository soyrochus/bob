"""Helper utilities for renderable server-side components."""

import logging
from typing import Callable, Dict

logger = logging.getLogger(__name__)

# Registry mapping component names to renderer callables
COMPONENTS: Dict[str, Callable[..., str]] = {}

def component(name: str) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """Register a component rendering function."""

    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        COMPONENTS[name] = func
        logger.debug("Registered component %s", name)
        return func

    return decorator


from pydantic import BaseModel, Field

class EmojiParams(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9_]+$")
    size: int = Field(24, ge=8, le=256)


@component("emoji")
def emoji_component(params: EmojiParams) -> str:
    """Render an emoji SVG tag."""
    return (
        f'<img src="/static/emoji/{params.name}.svg" '
        f'alt=":{params.name}:" '
        f'width="{params.size}" height="{params.size}" '
        'class="inline-block align-middle"/>'
    )
