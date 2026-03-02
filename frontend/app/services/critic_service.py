"""
Critic service — entry point for quality control and logical review.
"""

from __future__ import annotations

import logging
from app.agents.critic_agent import CriticAgent

logger = logging.getLogger(__name__)

async def perform_review(content: str) -> str:
    """
    Service wrapper for CriticAgent.review.
    """
    logger.debug("CriticService: Delegating review task to CriticAgent")
    agent = CriticAgent()
    return await agent.review(content)
