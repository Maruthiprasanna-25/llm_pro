import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.base import async_session_factory
from app.services.chat_service import process_chat
from app.models.user import User
from app.models.session import ChatSession
from app.models.message import Message
from sqlalchemy import select

async def repro():
    async with async_session_factory() as db:
        user_id = 1
        # Create a new session
        session = ChatSession(user_id=user_id, title="Repro Session")
        db.add(session)
        await db.commit()
        # Need a new session for processing chat to avoid state issues
    
    async with async_session_factory() as db:
        print(f"Sending message for binary sum...")
        user_msg = "test message for binary sum"
        
        # Use process_chat
        result = await process_chat(7, user_msg, user_id, db) # Using ID 7 which was "New Chat"
        print(f"Result: {result['message'][:50]}...")
        
        # Verify if title updated
        res = await db.execute(select(ChatSession).where(ChatSession.id == 7))
        session = res.scalar_one()
        print(f"Session 7 Title: {session.title}")
        
        msg_res = await db.execute(select(Message).where(Message.session_id == 7))
        msgs = msg_res.scalars().all()
        print(f"Total Messages in Session 7: {len(msgs)}")

if __name__ == "__main__":
    asyncio.run(repro())
