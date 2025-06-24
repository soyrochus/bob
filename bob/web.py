# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

"""FastAPI application wiring and route registration."""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession # Ensure AsyncSession is imported
from sqlalchemy.future import select
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError


from .db import engine, Base
from .models import User
from .shared import templates, HOME_PANELS, get_db, get_current_user # get_current_user is now a direct async function
from .conversations.routers import router as conversations_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan start, attempting to create tables.")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables should be created.")
    except Exception as e:
        print(f"Error during table creation: {e}")
    yield
    print("Lifespan end, disposing engine.")
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


app.add_middleware(SessionMiddleware, secret_key="change-me")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse("422.html", {"request": request}, status_code=422)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user or user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=302)


# Only keep mock and login/logout endpoints here

# Mock pages
@app.get("/training", response_class=HTMLResponse)
async def training(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("mock.html", {"request": request, "title": "Training"})


@app.get("/resources", response_class=HTMLResponse)
async def resources(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("mock.html", {"request": request, "title": "Resources"})


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("mock.html", {"request": request, "title": "Profile"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")


@app.get("/debug", response_class=HTMLResponse)
async def debug(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    return HTMLResponse(f"<pre>Session: {request.session}\\\\nUser: {user}</pre>")

# Include the conversations router
app.include_router(conversations_router)



