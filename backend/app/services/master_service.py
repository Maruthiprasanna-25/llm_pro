"""
Master service — entry point for request analysis by the Master Agent.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.master_agent import MasterAgent

logger = logging.getLogger(__name__)

async def analyze_request(goal: str) -> dict[str, Any]:
    """
    Service wrapper for MasterAgent.analyze_goal.
    This provides a clean interface for other services to use.
    """
    logger.debug("MasterService: Delegating goal analysis to MasterAgent")
    agent = MasterAgent()
    return await agent.analyze_goal(goal)
