"""Shared helpers for template rendering and database access."""

import json
from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi import Request
from .settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from .db import SessionLocal
from .models import User
from sqlalchemy.future import select

# Jinja2 templates
templates = Jinja2Templates(directory="bob/templates")
templates.env.globals["settings"] = settings

# Home panels data
HOME_PANELS = json.loads((Path(__file__).resolve().parent.parent / "home-panels.json").read_text())

# Async DB session generator (as a plain async generator function)
async def get_db(): # This is now an async generator function
    """Yield an ``AsyncSession`` and ensure it is closed."""
    session = SessionLocal()
    print(f"[DEBUG] get_db: Created session {type(session)}")
    try:
        yield session
    finally:
        print(f"[DEBUG] get_db: Closing session {type(session)}")
        await session.close()
        print("[DEBUG] get_db: Session closed")

# Async current user fetcher
async def get_current_user(request: Request, db: AsyncSession): # Removed Depends(get_db)
    """Return the logged in :class:`User` or ``None``."""
    user_id = request.session.get("user_id")
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    return None
