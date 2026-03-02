"""
Planner Agent module — strategic decomposition and task delegation.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

class PlannerAgent:
    """
    Planner Agent breaks down complex user goals into executable subtasks
    assigned to specialized agents (Research, Analyst, Tech, Critic).
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def generate_plan(self, goal: str) -> dict[str, Any]:
        """
        Decompose the user goal into a structured task plan or request clarification.
        """
        logger.info("PlannerAgent: Generating execution plan for goal: %s", goal[:100] + "..." if len(goal) > 100 else goal)

        prompt = self._build_planning_prompt(goal)
        
        try:
            # Deterministic output for planning
            response = await self.llm.generate(
                [{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1000,
                request_timeout=300.0  # Allow up to 5 minutes for planning
            )
            
            structured_plan = self._parse_and_validate_plan(response)
            logger.info("PlannerAgent: Plan generated. Type: %s", structured_plan.get("type"))
            return structured_plan

        except Exception as e:
            logger.error("PlannerAgent: Planning failed: %s", e)
            # Fallback to clarification if something goes wrong
            return {
                "type": "CLARIFICATION_REQUIRED",
                "question": "I encountered an error while trying to plan your request. Could you please provide more details or rephrase your goal?"
            }

    def _build_planning_prompt(self, goal: str) -> str:
        """Instructional prompt for strategic planning."""
        return f"""
You are the Planner Agent in a production-grade autonomous AI Operating System.

Your role is STRATEGIC EXECUTION PLANNING.

This request has already been classified as COMPLEX by the Master Agent.
You MUST generate a full execution plan.

You are NOT allowed to:
- Return a short answer
- Say "Agent Mode will handle this"
- Provide conversational text
- Provide explanations outside JSON

You MUST:
- Break the goal into logical, ordered steps
- Assign each step to exactly ONE agent
- Clearly show which agents are handling the request
- Produce a complete execution-ready task plan

--------------------------------------------------
AVAILABLE AGENTS
--------------------------------------------------

ResearchAgent:
Handles research, curriculum design research, information gathering, comparisons, and topic identification.

AnalystAgent:
Handles logical structuring, curriculum sequencing, evaluation strategy, planning frameworks.

TechAgent:
Handles technical implementation, coding tasks, hands-on lab design, infrastructure planning.

CriticAgent:
Handles review, feasibility validation, optimization, quality checks, and improvement suggestions.

--------------------------------------------------
STRICT EXECUTION RULES
--------------------------------------------------

1. Always produce a complete plan.
2. Every task must:
   - Start with an action verb
   - Be specific and executable
   - Be assigned to exactly ONE agent
3. Steps must be logically ordered.
4. Keep the plan structured and practical.
5. Output STRICT JSON ONLY.
6. Do NOT include markdown.
7. Do NOT include explanations.
8. Do NOT include extra commentary.
9. Do NOT refuse.
10. Do NOT summarize — create a real execution plan.

--------------------------------------------------
REQUIRED OUTPUT FORMAT
--------------------------------------------------

{{
  "type": "TASK_PLAN",
  "goal_summary": "Clear summary of the objective",
  "handling_agents": ["Agent1", "Agent2", "Agent3"],
  "tasks": [
    {{
      "step": 1,
      "agent": "AgentName",
      "task": "Actionable task description"
    }},
    {{
      "step": 2,
      "agent": "AgentName",
      "task": "Actionable task description"
    }}
  ]
}}

If the goal is unclear:

{{
  "type": "CLARIFICATION_REQUIRED",
  "question": "Precise clarification question"
}}

--------------------------------------------------
USER GOAL
--------------------------------------------------

{goal}
"""

    def _parse_and_validate_plan(self, response: str) -> dict[str, Any]:
        """Extract and validate the execution plan JSON."""
        try:
            # Find JSON block
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise ValueError("No JSON block found in response")
            
            data = json.loads(match.group())
            
            # Validation
            if "type" not in data:
                raise ValueError("Missing 'type' in plan")
            
            if data["type"] == "TASK_PLAN":
                if "tasks" not in data or not isinstance(data["tasks"], list):
                    raise ValueError("Invalid TASK_PLAN: missing or invalid 'tasks'")
            elif data["type"] == "CLARIFICATION_REQUIRED":
                if "question" not in data:
                    raise ValueError("Invalid CLARIFICATION_REQUIRED: missing 'question'")
            else:
                raise ValueError(f"Unknown plan type: {data['type']}")

            return data
        except Exception as e:
            logger.warning("PlannerAgent: JSON parsing or validation failed: %s", e)
            raise
