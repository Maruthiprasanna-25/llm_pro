"""
Chat request/response schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1)


class RoutingMetadata(BaseModel):
    decision: str
    reasoning: str
    recommended_mode: str


class ChatRequest(BaseModel):
    session_id: int
    message: str = Field(min_length=1, max_length=16_000)


class ChatResponse(BaseModel):
    session_id: int
    message: MessageSchema
    timestamp: datetime
    routing: Optional[RoutingMetadata] = None
    plan: Optional[dict[str, Any]] = None
