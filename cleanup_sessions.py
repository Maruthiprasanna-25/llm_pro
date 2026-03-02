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

async def cleanup_empty_sessions():
    async with async_session_factory() as db:
        # Find all sessions
        result = await db.execute(select(ChatSession))
        sessions = result.scalars().all()
        
        deleted_count = 0
        for s in sessions:
            # Check if session has any messages
            msg_result = await db.execute(select(Message).where(Message.session_id == s.id))
            messages = msg_result.scalars().all()
            
            if len(messages) == 0:
                print(f"Deleting empty session ID: {s.id} ('{s.title}')")
                await db.delete(s)
                deleted_count += 1
        
        await db.commit()
        print(f"Total empty sessions deleted: {deleted_count}")

if __name__ == "__main__":
    asyncio.run(cleanup_empty_sessions())
