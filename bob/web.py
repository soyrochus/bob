# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import SessionLocal, engine
from .models import Base, User, Conversation, Message
from .schemas import MessageCreate
from .chatgpt import chat

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="bob/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_or_create_user(db: Session) -> User:
    user = db.query(User).first()
    if not user:
        user = User(name="Ethan")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    user = await get_or_create_user(db)
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )

    if not conversations:
        conv = Conversation(title="New Conversation", user_id=user.id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversations = [conv]
    else:
        conv = conversations[0]

    messages = conv.messages if conv else []
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": conv,
            "messages": messages,
        },
    )


@app.get("/conversations/{conv_id}", response_class=HTMLResponse)
async def read_conversation(conv_id: int, request: Request, db: Session = Depends(get_db)):
    user = await get_or_create_user(db)
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    messages = conv.messages if conv else []
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": conv,
            "messages": messages,
        },
    )


@app.post("/conversations/{conv_id}/message", response_class=HTMLResponse)
async def send_message(conv_id: int, text: str = Form(...), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        return ""
    user_msg = Message(conversation_id=conv.id, sender="user", text=text)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    messages = [
        {"role": "system", "content": "You are Bob, an AI assistant."},
    ]
    for msg in conv.messages:
        role = "assistant" if msg.sender == "bob" else "user"
        messages.append({"role": role, "content": msg.text})
    messages.append({"role": "user", "content": text})

    bob_response = await chat(messages)
    bob_msg = Message(conversation_id=conv.id, sender="bob", text=bob_response)
    db.add(bob_msg)
    db.commit()
    db.refresh(bob_msg)

    return templates.TemplateResponse(
        "partials/messages.html",
        {"request": {}, "messages": [user_msg, bob_msg]},
    )


@app.post("/new-conversation", response_class=HTMLResponse)
async def new_conversation(request: Request, db: Session = Depends(get_db)):
    user = await get_or_create_user(db)
    conv = Conversation(title="New Conversation", user_id=user.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return templates.TemplateResponse(
        "partials/conversation_link.html",
        {"request": request, "conv": conv},
    )


@app.get("/conversations/search", response_class=HTMLResponse)
async def search_conversations(q: str, request: Request, db: Session = Depends(get_db)):
    user = await get_or_create_user(db)
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user.id,
            Conversation.title.ilike(f"%{q}%"),
        )
        .order_by(Conversation.created_at.desc())
        .all()
    )
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
async def training(request: Request):
    return templates.TemplateResponse("mock.html", {"request": request, "title": "Training"})


@app.get("/resources", response_class=HTMLResponse)
async def resources(request: Request):
    return templates.TemplateResponse("mock.html", {"request": request, "title": "Resources"})


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("mock.html", {"request": request, "title": "Profile"})
