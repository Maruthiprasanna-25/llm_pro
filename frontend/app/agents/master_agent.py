"""
Master Agent module — central intelligence controller for Campus AI OS.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

class MasterAgent:
    """
    Master Agent orchestrates the flow of user requests by analyzing their complexity
    using a cost-efficient hybrid logic (Fast Filter + LLM Classification).
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def analyze_goal(self, goal: str) -> dict[str, Any]:
        """
        Analyze user request semantically using LLM reasoning.
        1. Fast Filter: Short queries avoid LLM calls.
        2. LLM Classification: Semantic analysis for complexity.
        """
        # Step 1: Fast Filter (No LLM Call)
        words = goal.strip().split()
        if len(words) <= 6:
            logger.info("MasterAgent: Fast filter triggered (Short query).")
            return {
                "decision": "SIMPLE_REQUEST",
                "reasoning": "Short query detected.",
                "recommended_mode": "CHAT"
            }

        # Step 2: LLM Classification
        logger.info("MasterAgent: Proceeding to LLM classification.")
        prompt = self._build_classification_prompt(goal)
        
        try:
            # temperature=0.0, max_tokens=200 as requested
            response = await self.llm.generate(
                [{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=200,
                request_timeout=180.0  # Allow up to 3 minutes for classification
            )
            
            structured_data = self._parse_and_validate_json(response)
            logger.info("MasterAgent: Classification result: %s", structured_data["decision"])
            return structured_data

        except Exception as e:
            logger.error("MasterAgent: Classification or parsing failed: %s", e)
            # Fallback to SIMPLE_REQUEST as per safety requirements
            return {
                "decision": "SIMPLE_REQUEST",
                "reasoning": "Fallback due to analysis failure.",
                "recommended_mode": "CHAT"
            }

    def _build_classification_prompt(self, goal: str) -> str:
        """Instructional prompt for classification."""
        return f"""You are the Master Orchestrator of a Campus AI Operating System.

Your task is to classify the user's goal into one of two categories:

1. SIMPLE_REQUEST:
   - For greetings, general chat, or basic facts that do not require real-time data or planning.
   - Recommended mode: CHAT

2. COMPLEX_REQUEST:
   - For multi-step tasks, strategic planning, or deep technical analysis.
   - Recommended mode: AGENT

3. REAL_TIME_REQUEST:
   - For questions about current events, sports scores, stock prices, or recent news.
   - Requires web search.
   - Recommended mode: AGENT

Respond STRICTLY in valid JSON:

{{
  "decision": "SIMPLE_REQUEST" | "COMPLEX_REQUEST" | "REAL_TIME_REQUEST",
  "reasoning": "short explanation",
  "recommended_mode": "CHAT" | "AGENT",
  "intent": "static" | "search" | "analysis"
}}

User Goal:
{goal}"""

    def _parse_and_validate_json(self, response: str) -> dict[str, Any]:
        """Extract and validate JSON from LLM response."""
        try:
            # Find JSON block
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise ValueError("No JSON block found in response")
            
            data = json.loads(match.group())
            
            # Validation and correction
            decision = data.get("decision", "SIMPLE_REQUEST")
            if decision not in ["SIMPLE_REQUEST", "COMPLEX_REQUEST", "REAL_TIME_REQUEST"]:
                decision = "SIMPLE_REQUEST"
                
            mode = data.get("recommended_mode", "CHAT" if decision == "SIMPLE_REQUEST" else "AGENT")
            if mode not in ["CHAT", "AGENT"]:
                mode = "CHAT" if decision == "SIMPLE_REQUEST" else "AGENT"
                
            intent = data.get("intent", "static" if decision == "SIMPLE_REQUEST" else "analysis")
            reasoning = data.get("reasoning", "LLM based classification.")

            return {
                "decision": decision,
                "reasoning": reasoning,
                "recommended_mode": mode,
                "intent": intent
            }
        except Exception as e:
            logger.warning("MasterAgent: JSON parsing failed: %s", e)
            raise
