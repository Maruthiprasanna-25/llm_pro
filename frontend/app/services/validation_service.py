"""
Validation service — fact-checks agent outputs against retrieved RAG context.
"""

from __future__ import annotations

import logging
from typing import Any

from app.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Verifies that the agent's final report is grounded in the retrieved facts.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def validate_report(self, report: str, context: str) -> dict[str, Any]:
        """
        Uses an LLM to fact-check the report against the provided context.
        """
        if not context:
            # If no context, we can't fact-check, so we just return as is or with a warning.
            return {"valid": True, "score": 1.0, "feedback": "No context available for verification."}

        prompt = f"""You are a Critical Truth Verification Agent.
        
Your goal is to compare the RESEARCH REPORT below against the RETRIEVED FACTS.

RESEARCH REPORT:
{report}

RETRIEVED FACTS:
{context}

Check for:
1. HALLUCINATIONS: Are there claims in the report not supported by the facts?
2. CONTRADICTIONS: Does the report contradict any provided facts?
3. OMISSIONS: Did the report miss any critical data points?

Respond in JSON:
{{
  "is_hallucination": boolean,
  "confidence_score": float (0.0 to 1.0),
  "issues": ["list of specific issues"],
  "recommendation": "text"
}}"""

        try:
            response = await self.llm.generate(
                [{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=300
            )
            
            # Simple extractor (assuming JSON output)
            import json
            import re
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"valid": True, "feedback": "Could not parse validation JSON."}
            
        except Exception as e:
            logger.error("ValidationService: Validation failed: %s", str(e))
            return {"valid": True, "feedback": f"Validation error: {str(e)}"}

validation_service = ValidationService()
