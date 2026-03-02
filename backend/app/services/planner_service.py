"""
Planner service — entry point for task decomposition by the Planner Agent.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.planner_agent import PlannerAgent

logger = logging.getLogger(__name__)

async def generate_plan(goal: str) -> dict[str, Any]:
    """
    Service wrapper for PlannerAgent.generate_plan.
    """
    logger.debug("PlannerService: Delegating plan generation to PlannerAgent")
    agent = PlannerAgent()
    return await agent.generate_plan(goal)
