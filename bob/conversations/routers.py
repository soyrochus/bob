from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..shared import templates, HOME_PANELS, get_db, get_current_user  # get_current_user is now a direct async function
from .middleware import (
    get_conversations,
    get_conversation,
    create_conversation,
    save_user_message,
    stream_agent_response,
    search_conversations,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_conversations(
    request: Request,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    user = await get_current_user(request, db)  # Pass db to get_current_user
    print("[DEBUG] / called")
    print("[DEBUG] request:", request)
    print("[DEBUG] db:", db)
    print("[DEBUG] user:", user)
    if not user:
        print("[DEBUG] No user, redirecting to /login")
        return RedirectResponse("/login")
    conversations = await get_conversations(db, user)
    print("[DEBUG] conversations:", conversations)
    conv = conversations[0] if conversations else None
    print("[DEBUG] active_conversation:", conv)
    messages = conv.messages if conv else []
    print("[DEBUG] messages:", messages)
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


@router.get("/{conv_id}", response_class=HTMLResponse)
async def read_conversation(
    conv_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        return RedirectResponse("/login")
    conversations = await get_conversations(db, user)
    conv = await get_conversation(db, user, conv_id)
    messages = conv.messages if conv else []
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


@router.post("/{conv_id}/message", response_class=HTMLResponse)
async def send_message(
    request: Request,
    conv_id: int,
    text: str = Form(...),
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        return RedirectResponse("/login")
    msg = await save_user_message(db, conv_id, text)
    if not msg:
        return ""
    return templates.TemplateResponse(
        "partials/user_message_and_stream.html",
        {"request": {}, "msg": msg, "conv_id": conv_id},
    )


@router.get("/{conv_id}/stream")
async def stream_response(
    request: Request,
    conv_id: int,
    user_msg_id: int,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        async def empty():
            yield "data: [DONE]\n\n"

        return StreamingResponse(empty(), media_type="text/event-stream")
    generator = stream_agent_response(db, conv_id, user_msg_id)
    return StreamingResponse(generator, media_type="text/event-stream")


@router.post("/new", response_class=HTMLResponse)
async def new_conversation(
    request: Request,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        return RedirectResponse("/login")
    conv = await create_conversation(db, user)
    return templates.TemplateResponse(
        "partials/new_conversation.html",
        {"request": request, "conv": conv},
    )


@router.get("/search", response_class=HTMLResponse)
async def search(
    q: str,
    request: Request,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        return RedirectResponse("/login")
    conversations = await search_conversations(db, user, q)
    return templates.TemplateResponse(
        "partials/conversation_list.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": None,
        },
    )
