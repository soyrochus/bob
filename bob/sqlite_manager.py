from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .models import JobResponse, StatusEnum
from .settings import settings
from .task_manager import TaskManager

Base = declarative_base()


class SQLiteTask(Base):
    __tablename__ = "sqlite_tasks"

    id = Column(String, primary_key=True, index=True)
    payload = Column(JSON)
    status = Column(String)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


engine = create_async_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def _init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(_init_db())


class SingletonTasksManager(TaskManager):
    async def enqueue(self, payload: dict) -> JobResponse:
        try:
            job_id = str(uuid.uuid4())
            async with SessionLocal() as session:
                task = SQLiteTask(id=job_id, payload=payload, status=StatusEnum.PENDING.value)
                session.add(task)
                await session.commit()
            return JobResponse(job_id=job_id, status=StatusEnum.PENDING)
        except Exception as exc:  # pragma: no cover
            return JobResponse(job_id="", status=StatusEnum.FAILED, error=str(exc))

    async def status(self, job_id: str) -> JobResponse:
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(SQLiteTask).where(SQLiteTask.id == job_id))
                task = result.scalar_one_or_none()
                if not task:
                    return JobResponse(job_id=job_id, status=StatusEnum.FAILED, error="Job not found")
                return JobResponse(
                    job_id=task.id,
                    status=StatusEnum(task.status),
                    result=task.result,
                    error=task.error,
                )
        except Exception as exc:  # pragma: no cover
            return JobResponse(job_id=job_id, status=StatusEnum.FAILED, error=str(exc))
