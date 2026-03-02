"""
Synthesizer service — entry point for final report generation.
"""

from __future__ import annotations

import logging
from app.agents.synthesizer_agent import SynthesizerAgent

logger = logging.getLogger(__name__)

async def perform_synthesis(outputs: list[dict[str, str]]) -> str:
    """
    Service wrapper for SynthesizerAgent.synthesize.
    """
    logger.debug("SynthesizerService: Delegating synthesis task to SynthesizerAgent")
    agent = SynthesizerAgent()
    return await agent.synthesize(outputs)
