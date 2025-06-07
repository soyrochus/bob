"""Token expansion pipeline for server-side components."""

from __future__ import annotations

import logging
import re

import bleach
from pydantic import ValidationError

from .components import COMPONENTS, EmojiParams

logger = logging.getLogger(__name__)

TOKEN_RE = re.compile(r"\[\[component:(?P<name>[a-z0-9_]+)(?P<params>[^\]]*)]]")

ALLOWED_TAGS = ["img"]
ALLOWED_ATTRS = {"img": ["src", "alt", "width", "height", "class"]}


def _parse_params(param_str: str) -> dict[str, str]:
    params: dict[str, str] = {}
    for part in param_str.strip().split():
        if "=" in part:
            k, v = part.split("=", 1)
            params[k] = v.strip('"')
    return params


def expand_tokens(text: str) -> str:
    """Expand registered component tokens in the given text."""

    def _replace(match: re.Match[str]) -> str:
        name = match.group("name")
        params_str = match.group("params")
        params = _parse_params(params_str)
        renderer = COMPONENTS.get(name)
        if not renderer:
            return f"<code>⚠ Unknown component '{name}'</code>"
        try:
            if name == "emoji":
                model = EmojiParams(**params)
                html = renderer(model)
            else:
                html = renderer(**params)
            return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)
        except ValidationError as exc:
            return f"<code>⚠ {exc.errors()[0]['msg']}</code>"
        except Exception as exc:  # pragma: no cover - unexpected errors
            logger.exception("Component rendering failed")
            return f"<code>⚠ {exc}</code>"

    return TOKEN_RE.sub(_replace, text)
