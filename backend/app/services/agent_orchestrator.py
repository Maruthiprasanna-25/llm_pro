"""
Agent Orchestrator — manages the lifecycle of multi-agent tasks and tool loops.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.research_service import perform_research
from app.services.tool_execution_service import tool_execution_service
from app.services.analyst_service import perform_analysis
from app.services.tech_service import perform_tech_task
from app.services.critic_service import perform_review
from app.services.synthesizer_service import perform_synthesis
from app.services.validation_service import validation_service
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Executes a structured task plan by delegating to specialized agents 
     and handling iterative tool-use loops.
    """

    async def execute_plan(self, plan: dict[str, Any]) -> str:
        """
        Iterates through tasks in the plan, executes them, and returns a final synthesis.
        """
        if plan.get("type") == "CLARIFICATION_REQUIRED":
            return plan.get("question", "I need more information to proceed.")

        if plan.get("type") != "TASK_PLAN":
            return "Unable to execute non-standard plan."

        tasks = plan.get("tasks", [])
        task_results = []

        logger.info("AgentOrchestrator: Executing plan with %d tasks", len(tasks))

        for task in tasks:
            agent_type = task.get("agent", "").lower()
            description = task.get("description", "")
            
            logger.info("AgentOrchestrator: Delegating to %s: %s", agent_type, description[:50])
            
            result = await self._execute_agent_task(agent_type, description)
            task_results.append({
                "agent": agent_type,
                "task": description,
                "output": result
            })

        # Final Synthesis
        logger.info("AgentOrchestrator: Synthesizing results...")
        report = await perform_synthesis(task_results)

        # Validation (Phase 3)
        # Collect all context retrieved during search tasks
        search_results = [r for r in task_results if r["agent"] == "research"]
        total_context = ""
        for res in search_results:
             query = res.get("task", "")
             total_context += await rag_service.query(query, n_results=5)
        
        if total_context:
            logger.info("AgentOrchestrator: Validating report against %d context chars", len(total_context))
            validation = await validation_service.validate_report(report, total_context)
            if validation.get("is_hallucination"):
                logger.warning("AgentOrchestrator: Potential hallucination detected. Appending warning.")
                report += "\n\n> [!CAUTION]\n> This report contains claims that may not be fully supported by official sources. Please verify critical data points."

        return report

    async def _execute_agent_task(self, agent: str, task_description: str) -> str:
        """
        Calls a specific agent and handles tool-use loops if the agent requests them.
        """
        # 1. Initial call to the agent
        if agent == "research":
            current_output = await perform_research(task_description)
        elif agent == "analyst":
            current_output = await perform_analysis(task_description)
        elif agent == "tech":
            current_output = await perform_tech_task(task_description)
        elif agent == "critic":
            current_output = await perform_review(task_description)
        else:
            return f"Error: Unknown agent {agent}"

        # 2. Tool-Use Loop (Max 3 iterations for safety)
        for _ in range(3):
            tool_calls = await tool_execution_service.execute_tools(current_output)
            if not tool_calls:
                break
            
            logger.info("AgentOrchestrator: Processing %d tool results for %s", len(tool_calls), agent)
            
            # Construct context from tool results
            tool_context = "\n--- Tool Results ---\n"
            for t in tool_calls:
                tool_context += f"Tool: {t['tool']}\nResult: {t['result']}\n\n"
            
            # Feed results back to the agent
            # Note: We append the tool results to the description to give the agent context of what's already found.
            feedback_prompt = f"{task_description}\n\nExisting Progress:\n{current_output}\n\n{tool_context}\n\nPlease proceed based on these results."
            
            if agent == "research":
                current_output = await perform_research(feedback_prompt)
            elif agent == "analyst":
                current_output = await perform_analysis(feedback_prompt)
            elif agent == "tech":
                current_output = await perform_tech_task(feedback_prompt)
            # Critic usually doesn't call tools in this flow
            else:
                break

        return current_output

orchestrator = AgentOrchestrator()
