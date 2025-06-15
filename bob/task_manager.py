from __future__ import annotations

from abc import ABC, abstractmethod

from .models import JobResponse


class TaskManager(ABC):
    @abstractmethod
    async def enqueue(self, payload: dict) -> JobResponse:
        ...

    @abstractmethod
    async def status(self, job_id: str) -> JobResponse:
        ...
