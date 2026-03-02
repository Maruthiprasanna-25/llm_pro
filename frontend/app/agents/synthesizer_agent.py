"""
Synthesizer Agent module — specialized final output and reporting agent.
"""

from __future__ import annotations

import logging
from typing import Any

from app.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

class SynthesizerAgent:
    """
    Synthesizer Agent combines all agent outputs into a professional final report.
    It ensures coherence, removes redundancy, and applies executive formatting.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def synthesize(self, outputs: list[dict[str, str]]) -> str:
        """
        Merge multiple agent outputs into a final report.
        """
        logger.info("SynthesizerAgent: Synthesizing %d outputs", len(outputs))
        
        formatted_inputs = ""
        for item in outputs:
            agent_name = item.get("agent", "Unknown Agent")
            content = item.get("content", "")
            formatted_inputs += f"=== AGENT: {agent_name} ===\n{content}\n\n"
        
        prompt = self._build_synthesizer_prompt()
        
        try:
            # Synthesis requires creative formatting and coherence.
            response = await self.llm.generate(
                [{"role": "system", "content": prompt}, {"role": "user", "content": f"Combine these results into a FINAL REPORT:\n\n{formatted_inputs}"}],
                temperature=0.3, # Slightly higher for better flow
                max_tokens=4000,
                request_timeout=600.0  # Synthesis of long reports can take time
            )
            
            return response

        except Exception as e:
            logger.error("SynthesizerAgent: Synthesis failed: %s", e)
            return f"Error: Unable to complete synthesis due to {str(e)}"

    def _build_synthesizer_prompt(self) -> str:
        """Instructional prompt for the Synthesizer Agent."""
        return """You are the Synthesizer Agent.

Your role is to combine all specialist agent outputs into a professional, cohesive, and executive-ready final report.

Rules:
- Remove redundant information across agent outputs.
- Ensure logical coherence and smooth transitions.
- Produce executive-level formatting (headers, bullet points, clean structure).

Output structure:
FINAL REPORT
[Professional Title]

Executive Summary:
[High-level overview]

Detailed Findings:
[Structured merger of specialist insights]

Recommendations & Next Steps:
[Actionable summary]

Maintain a professional, authoritative, and concise tone."""
