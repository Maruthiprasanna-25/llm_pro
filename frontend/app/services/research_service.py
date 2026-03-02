"""
Research service — entry point for market and knowledge research.
"""

from __future__ import annotations

import logging
from app.agents.research_agent import ResearchAgent

logger = logging.getLogger(__name__)

async def perform_research(task: str) -> str:
    """
    Service wrapper for ResearchAgent.execute_research.
    """
    logger.debug("ResearchService: Delegating research task to ResearchAgent")
    agent = ResearchAgent()
    return await agent.execute_research(task)
