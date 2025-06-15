# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

"""Bob web application."""

from .web import app
from .tasks.redis_manager import RedisTasksManager
from .tasks.sqlite_manager import SingletonTasksManager

__all__ = ["app"]
