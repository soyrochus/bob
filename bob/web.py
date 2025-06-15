# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

import json
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from starlette.middleware.sessions import SessionMiddleware

from .db import SessionLocal, engine, Base
from .models import User, Conversation, Message
from .schemas import MessageCreate
from .llm import stream_tokens
from .token_expander import expand_tokens

app = FastAPI()

# Signed cookie session for login state
app.add_middleware(SessionMiddleware, secret_key="change-me")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="bob/templates")
HOME_PANELS = json.loads((Path(__file__).resolve().parent.parent / "home-panels.json").read_text())


# Fix get_db to be an async generator
async def get_db():
    async with SessionLocal() as session:
        yield session


# Refactor get_current_user to async
async def get_current_user(request: Request, db: AsyncSession) -> User | None:
    user_id = request.session.get("user_id")
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    return None


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        user = User()
        user.username = username
        user.password = password
        user.name = username
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif user.password != password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=302)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()
    conv = conversations[0] if conversations else None
    messages = conv.messages if conv else []
    for m in messages:
        m.html = expand_tokens(m.text)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": conv,
            "messages": messages,
            "home_panels": HOME_PANELS,
        },
    )


@app.get("/conversations/{conv_id}", response_class=HTMLResponse)
async def read_conversation(conv_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conv_id)
    )
    conv = result.scalars().first()
    messages = conv.messages if conv else []
    for m in messages:
        m.html = expand_tokens(m.text)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": conv,
            "messages": messages,
            "home_panels": HOME_PANELS,
        },
    )


@app.post("/conversations/{conv_id}/message", response_class=HTMLResponse)
async def send_message(request: Request, conv_id: int, text: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalars().first()
    if not conv:
        return ""
    user_msg = Message()
    user_msg.conversation_id = conv.id
    user_msg.sender = "user"
    user_msg.text = text
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)
    user_msg.html = expand_tokens(user_msg.text)
    return templates.TemplateResponse(
        "partials/user_message_and_stream.html",
        {"request": {}, "msg": user_msg, "conv_id": conv.id},
    )


@app.get("/conversations/{conv_id}/stream")
async def stream_response(request: Request, conv_id: int, user_msg_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        async def empty():
            yield "data: [DONE]\n\n"
        return StreamingResponse(empty(), media_type="text/event-stream")
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalars().first()
    result = await db.execute(select(Message).where(Message.id == user_msg_id))
    user_msg = result.scalars().first()
    if not conv or not user_msg:
        async def empty():
            yield "data: [DONE]\n\n"
        return StreamingResponse(empty(), media_type="text/event-stream")
    result = await db.execute(select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at))
    history = result.scalars().all()
    messages = [{"role": "system", "content": "You are Bob, an AI assistant."}]
    for msg in history:
        role = "assistant" if msg.sender == "bob" else "user"
        messages.append({"role": role, "content": msg.text})
    async def event_generator():
        full_text = ""
        async for chunk in stream_tokens(messages):
            full_text += chunk
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
        bob_msg = Message()
        bob_msg.conversation_id = conv.id
        bob_msg.sender = "bob"
        bob_msg.text = full_text
        db.add(bob_msg)
        await db.commit()
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/new-conversation", response_class=HTMLResponse)
async def new_conversation(request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    conv = Conversation()
    conv.title = "New Conversation"
    conv.user_id = user.id
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return templates.TemplateResponse(
        "partials/new_conversation.html",
        {"request": request, "conv": conv},
    )


@app.get("/conversations/search", response_class=HTMLResponse)
async def search_conversations(q: str, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse("/login")
    result = await db.execute(select(Conversation).where(
        Conversation.user_id == user.id,
        Conversation.title.ilike(f"%{q}%")
    ).order_by(Conversation.created_at.desc()))
    conversations = result.scalars().all()
    return templates.TemplateResponse(
        "partials/conversation_list.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": None,
        },
    )


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


# Fix async model creation
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

import asyncio
asyncio.run(init_models())
