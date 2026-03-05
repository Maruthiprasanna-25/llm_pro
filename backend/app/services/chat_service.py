"""
Chat service — orchestrates message persistence and LLM calls.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.llm.factory import get_llm_provider
from app.models.message import Message
from app.models.session import ChatSession
from app.services.agent_orchestrator import orchestrator
from app.services.shield_service import shield_service
from app.utils.exceptions import LLMError, NotFoundError, SecurityError

logger = logging.getLogger(__name__)


async def _get_session_with_messages(
    session_id: int,
    user_id: int,
    db: AsyncSession,
) -> ChatSession:
    """Fetch session with messages, verify ownership."""
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise NotFoundError("Session not found")
    return session


def _build_llm_messages(session: ChatSession) -> list[dict]:
    """Convert ORM messages to the list[dict] format LLM providers expect."""
    return [
        {"role": msg.role, "content": msg.content}
        for msg in session.messages
    ]


async def process_chat(
    session_id: int,
    user_message: str,
    user_id: int,
    db: AsyncSession,
) -> dict[str, Any]:
    """
    1. Save user message
    2. Analyze complexity
    3. Call LLM or return Agent Mode placeholder
    4. Save and return response with routing metadata
    """
    session = await _get_session_with_messages(session_id, user_id, db)

    # Enterprise Guardrail: Semantic Inspection
    if not await shield_service.inspect_input(user_message):
        raise SecurityError("Input blocked by enterprise security policy.")

    # Persist user message
    user_msg = Message(
        session_id=session_id,
        role="user",
        content=user_message,
    )
    db.add(user_msg)
    await db.flush()
    session.messages.append(user_msg)

    # Master Agent Analysis
    routing_result = await analyze_request(user_message)
    
    if routing_result.get("recommended_mode") == "AGENT":
        # Generate Strategic Plan
        plan = await generate_plan(user_message)
        
        if plan.get("type") == "CLARIFICATION_REQUIRED":
            content = plan.get("question", "I need some clarification to proceed.")
        else:
            # Execute the Plan via Orchestrator
            content = await orchestrator.execute_plan(plan)

        agent_msg = Message(
            session_id=session_id,
            role="assistant",
            content=content,
        )
        db.add(agent_msg)
        await db.commit()
        return {
            "message": content,
            "routing": routing_result,
            "plan": plan,
            "timestamp": agent_msg.timestamp
        }

    # Call LLM (Normal Chat Mode)
    llm = get_llm_provider()
    messages = _build_llm_messages(session)

    try:
        reply_text = await llm.generate(messages)
    except Exception as exc:
        logger.error("LLM generate failed: %s", exc)
        raise LLMError(f"LLM error: {exc}") from exc

    # Persist assistant message
    assistant_msg = Message(
        session_id=session_id,
        role="assistant",
        content=reply_text,
    )
    db.add(assistant_msg)
    await db.flush()
    await db.refresh(assistant_msg)

    # Auto-title the session from first exchange
    if session.title == "New Chat" or not session.title:
        session.title = user_message[:80]
        await db.flush()
    
    await db.commit()

    logger.info("Chat processed: session=%d routing=%s", session_id, routing_result["decision"])
    return {
        "message": reply_text,
        "routing": routing_result,
        "plan": None,
        "timestamp": assistant_msg.timestamp
    }


async def process_chat_stream(
    session_id: int,
    user_message: str,
    user_id: int,
    db: AsyncSession,
) -> AsyncIterator[str]:
    """
    Streaming variant:
    1. Save user message
    2. Yield tokens from LLM
    3. Assemble and save assistant message after stream completes
    """
    session = await _get_session_with_messages(session_id, user_id, db)

    user_msg = Message(
        session_id=session_id,
        role="user",
        content=user_message,
    )
    db.add(user_msg)
    await db.flush()
    session.messages.append(user_msg)

    # Master Agent Analysis
    routing_result = await analyze_request(user_message)
    if routing_result.get("recommended_mode") == "AGENT":
        # Yield special indicator or the final message
        # For simplicity and to avoid breaking SSE, we'll yield the text.
        # Routing metadata for streaming might need a more complex SSE protocol,
        # but here we'll follow the AGENT mode return rule.
        yield "Agent Mode will handle this request."
        
        reply_text = "Agent Mode will handle this request."
        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=reply_text,
        )
        db.add(assistant_msg)
        await db.commit()
        return

    llm = get_llm_provider()
    messages = _build_llm_messages(session)

    full_reply: list[str] = []

    try:
        async for token in llm.stream(messages):
            full_reply.append(token)
            yield token
    except Exception as exc:
        logger.error("LLM stream failed: %s", exc)
        raise LLMError(f"LLM stream error: {exc}") from exc

    # Persist complete assistant reply
    reply_text = "".join(full_reply)
    assistant_msg = Message(
        session_id=session_id,
        role="assistant",
        content=reply_text,
    )
    db.add(assistant_msg)

    if session.title == "New Chat" or not session.title:
        session.title = user_message[:80]

    await db.commit()
    logger.info("Stream completed: session=%d chars=%d", session_id, len(reply_text))
