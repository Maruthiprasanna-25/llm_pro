"""
Critic Agent module — specialized quality control and logical review agent.
"""

from __future__ import annotations

import logging
from typing import Any

from app.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

class CriticAgent:
    """
    Critic Agent identifies logical flaws, hallucinations, and missing steps.
    It produces structured "CRITIC REVIEW" reports.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def review(self, content: str) -> str:
        """
        Review a given content or plan.
        """
        logger.info("CriticAgent: Reviewing content (length: %d)", len(content))
        
        prompt = self._build_critic_prompt()
        
        try:
            # Criticism needs high reasoning and the model should be strict.
            response = await self.llm.generate(
                [{"role": "system", "content": prompt}, {"role": "user", "content": f"Please review the following content:\n\n{content}"}],
                temperature=0.1,
                max_tokens=2000,
                request_timeout=300.0
            )
            
            return response

        except Exception as e:
            logger.error("CriticAgent: Review failed: %s", e)
            return f"Error: Unable to complete review due to {str(e)}"

    def _build_critic_prompt(self) -> str:
        """Instructional prompt for the Critic Agent."""
        return """You are a Critical Review Agent.

Your job:
- Identify logical flaws.
- Detect hallucinations (fabricated info).
- Find missing steps in a process or plan.
- Challenge unrealistic expectations or plans.

Rules:
- Be strict and objective.
- Suggest specific corrections.
- NEVER rewrite full solutions — only provide critical feedback.

Output format:
CRITIC REVIEW:
- Issues found: <Detailed list of problems>
- Why they matter: <Impact of these issues>
- Suggested fixes: <Precise improvements>

Focus on quality control and logical integrity."""
