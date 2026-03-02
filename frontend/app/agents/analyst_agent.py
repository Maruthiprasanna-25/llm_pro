"""
Analyst Agent module — specialized business and technical analysis agent.
"""

from __future__ import annotations

import logging
from typing import Any

from app.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

class AnalystAgent:
    """
    Analyst Agent evaluates feasibility, identifies risks, and estimates timelines.
    It produces structured "ANALYSIS REPORT" reports.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def analyze(self, task: str) -> str:
        """
        Perform analysis on a given task/goal.
        """
        logger.info("AnalystAgent: Performing analysis on task: %s", task[:100])
        
        prompt = self._build_analyst_prompt()
        
        try:
            # Analysis needs high reasoning and precision.
            response = await self.llm.generate(
                [{"role": "system", "content": prompt}, {"role": "user", "content": task}],
                temperature=0.1,
                max_tokens=2000,
                request_timeout=300.0
            )
            
            return response

        except Exception as e:
            logger.error("AnalystAgent: Analysis failed: %s", e)
            return f"Error: Unable to complete analysis due to {str(e)}"

    def _build_analyst_prompt(self) -> str:
        """Instructional prompt for the Analyst Agent."""
        return """You are a Business & Technical Analyst Agent.

Your responsibilities:
- Evaluate feasibility.
- Identify risks.
- Estimate timelines.
- Perform SWOT-style reasoning.

Rules:
- Always justify conclusions.
- Highlight assumptions.
- Flag unrealistic expectations.

Output format:
ANALYSIS REPORT:
- Feasibility: <Your evaluation>
- Risks: <Identification of risks>
- Constraints: <Resource or technical constraints>
- Recommendations: <Your strategic advice>

Be analytical, concise, and professional."""
