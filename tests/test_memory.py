import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from bob.models import Base, User, Conversation, Message
from bob.conversations.middleware import get_history, HISTORY_LIMIT

@pytest.mark.asyncio
async def test_get_history_limit():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        user = User(name="u", username="u", password="pw")
        session.add(user)
        await session.commit()
        await session.refresh(user)

        conv = Conversation(title="t", user_id=user.id)
        session.add(conv)
        await session.commit()
        await session.refresh(conv)

        for i in range(25):
            session.add(Message(conversation_id=conv.id, sender="user", text=f"m{i}"))
        await session.commit()

        history = await get_history(session, conv.id, limit=HISTORY_LIMIT)
        assert len(history) == HISTORY_LIMIT
        assert history[0].text == "m5"
        assert history[-1].text == "m24"
