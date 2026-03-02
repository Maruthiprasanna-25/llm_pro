import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from sqlalchemy import select
from app.db.base import async_session_factory
from app.models.user import User
from app.models.session import ChatSession
from app.models.message import Message

async def dump_all_messages():
    async with async_session_factory() as db:
        result = await db.execute(select(Message).order_by(Message.id))
        messages = result.scalars().all()
        print(f"--- All Messages ({len(messages)}) ---")
        for m in messages:
            print(f"ID: {m.id}, SessionID: {m.session_id}, Role: {m.role}, Content: {m.content[:100]}...")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(dump_all_messages())
