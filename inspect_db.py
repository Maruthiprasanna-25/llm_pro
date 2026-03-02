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

async def inspect_db():
    async with async_session_factory() as db:
        # Fetch users
        user_result = await db.execute(select(User))
        users = user_result.scalars().all()
        print(f"--- Users ({len(users)}) ---")
        for u in users:
            print(f"ID: {u.id}, Email: {u.email}")
        
        # Fetch sessions
        result = await db.execute(select(ChatSession))
        sessions = result.scalars().all()
        print(f"\n--- Sessions ({len(sessions)}) ---")
        for s in sessions:
            print(f"ID: {s.id}, Title: {s.title}, UserID: {s.user_id}")
            
            # Fetch messages
            msg_result = await db.execute(
                select(Message).where(Message.session_id == s.id).order_by(Message.timestamp)
            )
            messages = msg_result.scalars().all()
            print(f"  Messages ({len(messages)}):")
            for m in messages:
                print(f"    [{m.role}] {m.content[:100]}...")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(inspect_db())
