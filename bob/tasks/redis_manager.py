"""Task queue backed by Redis."""

# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | License: MIT
from __future__ import annotations

import json
import uuid

from redis.asyncio import Redis

from ..models import JobResponse, StatusEnum
from ..settings import settings
from . import TaskManager


class RedisTasksManager(TaskManager):
    def __init__(self) -> None:
        self.redis = Redis.from_url(settings.REDIS_URL)

    async def enqueue(self, payload: dict) -> JobResponse:
        try:
            job_id = str(uuid.uuid4())
            await self.redis.hset(f"jobs:{job_id}", mapping={"status": StatusEnum.PENDING.value})
            await self.redis.lpush("tasks_queue", json.dumps({"job_id": job_id, "payload": payload}))
            return JobResponse(job_id=job_id, status=StatusEnum.PENDING)
        except Exception as exc:  # pragma: no cover - network errors
            return JobResponse(job_id="", status=StatusEnum.FAILED, error=str(exc))

    async def status(self, job_id: str) -> JobResponse:
        try:
            data = await self.redis.hgetall(f"jobs:{job_id}")
            if not data:
                return JobResponse(job_id=job_id, status=StatusEnum.FAILED, error="Job not found")
            status = StatusEnum(data.get(b"status").decode())
            result = data.get(b"result")
            error = data.get(b"error")
            return JobResponse(
                job_id=job_id,
                status=status,
                result=json.loads(result) if result else None,
                error=error.decode() if error else None,
            )
        except Exception as exc:  # pragma: no cover - network errors
            return JobResponse(job_id=job_id, status=StatusEnum.FAILED, error=str(exc))
