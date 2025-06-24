from __future__ import annotations

from typing import AsyncGenerator, Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models import Conversation, Message, User
from ..token_expander import expand_tokens
from ..agents import get_agent
from ..db import SessionLocal

# Number of recent messages to include as conversation history
HISTORY_LIMIT = 20


async def get_history(db: AsyncSession, conv_id: int, limit: int = HISTORY_LIMIT) -> list[Message]:
    """Return the last ``limit`` messages for the given conversation in chronological order."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conv_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return list(reversed(result.scalars().all()))


async def get_conversations(db: AsyncSession, user: User) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()
    for conv in conversations:
        for msg in conv.messages:
            msg.html = expand_tokens(msg.text)
    return conversations


async def get_conversation(db: AsyncSession, user: User, conv_id: int) -> Conversation | None:
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conv_id, Conversation.user_id == user.id)
    )
    conv = result.scalars().first()
    if conv:
        for msg in conv.messages:
            msg.html = expand_tokens(msg.text)
    return conv


async def create_conversation(db: AsyncSession, user: User) -> Conversation:
    conv = Conversation(title="New Conversation", user_id=user.id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def save_user_message(db: AsyncSession, conv_id: int, text: str) -> Message | None:
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalars().first()
    if not conv:
        return None
    user_msg = Message(conversation_id=conv.id, sender="user", text=text)
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)
    user_msg.html = expand_tokens(user_msg.text)
    return user_msg


async def stream_agent_response(
    db: AsyncSession, conv_id: int, user_msg_id: int, agent_name: str
) -> AsyncGenerator[str, None]:
    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalars().first()
    result = await db.execute(select(Message).where(Message.id == user_msg_id))
    user_msg = result.scalars().first()
    if not conv or not user_msg:
        yield "data: [DONE]\n\n"
        return

    history = await get_history(db, conv.id)
    messages: list[dict[str, str]] = [{"role": "system", "content": "You are Bob, an AI assistant."}]
    for msg in history:
        role = "assistant" if msg.sender == "bob" else "user"
        messages.append({"role": role, "content": msg.text})

    agent = get_agent(agent_name)
    print(f"Using agent: {agent_name}")
    full_text = ""
    async for chunk in agent.stream(messages):
        full_text += chunk
        yield f"data: {chunk}\n\n"

    async with SessionLocal() as new_session:
        bob_msg = Message(conversation_id=conv.id, sender="bob", text=full_text)
        new_session.add(bob_msg)
        await new_session.commit()

    yield "data: [DONE]\n\n"


async def search_conversations(db: AsyncSession, user: User, query: str) -> list[Conversation]:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id, Conversation.title.ilike(f"%{query}%"))
        .order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()


async def delete_conversation(db: AsyncSession, user: User, conv_id: int) -> bool:
    """Delete a conversation owned by the given user."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conv_id, Conversation.user_id == user.id)
    )
    conv = result.scalars().first()
    if not conv:
        return False
    await db.delete(conv)
    await db.commit()
    return True
