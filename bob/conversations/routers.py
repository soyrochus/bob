"""HTTP routes for conversation management and chat interface."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import Conversation, User
from ..shared import templates, HOME_PANELS, get_db, get_current_user  # get_current_user is now a direct async function
from ..settings import settings
from ..agents import get_selector_choices
from .middleware import (
    get_conversations,
    get_conversation,
    create_conversation,
    save_user_message,
    stream_agent_response,
    search_conversations,
    delete_conversation,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def list_conversations(
    request: Request,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    """Render the home page showing the latest conversation list."""
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
    agent_names = get_selector_choices()
    active_agent = request.session.get("agent", agent_names[0][0] if agent_names else "default")
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": conv,
            "messages": messages,
            "home_panels": HOME_PANELS,
            "agent_names": agent_names,
            "active_agent": active_agent,
        },
    )


@router.get("/{conv_id}", response_class=HTMLResponse)
async def read_conversation(
    conv_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    """Display a single conversation and its messages."""
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        return RedirectResponse("/login")
    conversations = await get_conversations(db, user)
    conv = await get_conversation(db, user, conv_id)
    messages = conv.messages if conv else []
    agent_names = get_selector_choices()
    active_agent = request.session.get("agent", agent_names[0][0] if agent_names else "default")
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "conversations": conversations,
            "active_conversation": conv,
            "messages": messages,
            "home_panels": HOME_PANELS,
            "agent_names": agent_names,
            "active_agent": active_agent,
        },
    )


@router.post("/{conv_id}/message", response_class=HTMLResponse)
async def send_message(
    request: Request,
    conv_id: int,
    agent: str = Form("default"),
    text: str = Form(...),
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    """Persist a message and return markup for streaming the reply."""
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        return RedirectResponse("/login")
    request.session["agent"] = agent
    msg = await save_user_message(db, conv_id, text)
    if not msg:
        return ""
    return templates.TemplateResponse(
        "partials/user_message_and_stream.html",
        {"request": {}, "msg": msg, "conv_id": conv_id, "agent": agent},
    )


@router.get("/{conv_id}/stream")
async def stream_response(
    request: Request,
    conv_id: int,
    user_msg_id: int,
    agent: str = "default",
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    """Server-sent events endpoint for agent streaming."""
    user = await get_current_user(request, db)  # Pass db to get_current_user
    if not user:
        async def empty():
            yield "data: [DONE]\n\n"

        return StreamingResponse(empty(), media_type="text/event-stream")
    generator = stream_agent_response(db, conv_id, user_msg_id, agent)
    return StreamingResponse(generator, media_type="text/event-stream")


@router.post("/new", response_class=HTMLResponse)
async def new_conversation(
    request: Request,
    db: AsyncSession = Depends(get_db),  # Inject db session here
):
    """Create a new conversation and return the rendered list item."""
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
    """Return conversations matching ``q`` rendered as a partial list."""
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


@router.post("/{conv_id}/rename", response_class=HTMLResponse)
async def rename_conversation(
    conv_id: int,
    request: Request,
    title: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Rename a conversation and return the updated list item."""
    user = await get_current_user(request, db)
    if not user:
        return HTMLResponse(status_code=403, content="Not authorized")
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.user_id == user.id)
    )
    conv = result.scalars().first()
    if not conv:
        return HTMLResponse(status_code=404, content="")
    conv.title = title
    await db.commit()
    await db.refresh(conv)
    return templates.TemplateResponse(
        "partials/conversation_item.html",
        {"request": request, "conv": conv, "active_conversation": None},
    )


@router.post("/{conv_id}/delete", response_class=HTMLResponse)
async def delete_conversation_route(
    conv_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Delete ``conv_id`` and redirect to the conversation list."""
    user = await get_current_user(request, db)
    if not user:
        return HTMLResponse(status_code=403, content="Not authorized")
    success = await delete_conversation(db, user, conv_id)
    if not success:
        return HTMLResponse(status_code=404, content="")
    # Redirect the user back to the conversation list after deletion
    return RedirectResponse("/", status_code=303)
