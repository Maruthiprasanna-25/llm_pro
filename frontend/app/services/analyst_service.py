"""
Analyst service — entry point for business and technical analysis.
"""

from __future__ import annotations

import logging
from app.agents.analyst_agent import AnalystAgent

logger = logging.getLogger(__name__)

async def perform_analysis(task: str) -> str:
    """
    Service wrapper for AnalystAgent.analyze.
    """
    logger.debug("AnalystService: Delegating analysis task to AnalystAgent")
    agent = AnalystAgent()
    return await agent.analyze(task)
