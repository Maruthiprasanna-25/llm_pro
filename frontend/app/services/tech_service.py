"""
Tech service — entry point for software engineering and implementation tasks.
"""

from __future__ import annotations

import logging
from app.agents.tech_agent import TechAgent

logger = logging.getLogger(__name__)

async def perform_tech_task(task: str) -> str:
    """
    Service wrapper for TechAgent.execute_task.
    """
    logger.debug("TechService: Delegating technical task to TechAgent")
    agent = TechAgent()
    return await agent.execute_task(task)
