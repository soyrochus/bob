# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

"""Top-level package for the Bob web application.

This module exposes the :data:`~bob.web.app` FastAPI instance so it can be
imported by ASGI servers.  The task managers are imported here as a convenience
for other modules that need to enqueue background jobs.
"""

from .web import app
from .tasks.redis_manager import RedisTasksManager
from .tasks.sqlite_manager import SingletonTasksManager

__all__ = ["app"]
