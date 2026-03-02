"""
Tool execution service — interprets and executes agent-requested tool calls.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.services.search_service import search_service
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class ToolExecutionService:
    """
    Orchestrates the execution of tools (search, retrieve) identified by agents.
    """

    async def execute_tools(self, response_text: str) -> list[dict[str, Any]]:
        """
        Parses the agent's response for tool call JSON blocks and executes them.
        Returns a list of tool results.
        """
        tool_results = []
        
        # Look for JSON blocks in the response
        # Matches: { "action": "...", "action_input": "..." }
        json_matches = re.finditer(r"(\{.*?\})", response_text, re.DOTALL)
        
        for match in json_matches:
            try:
                data = json.loads(match.group(1))
                action = data.get("action")
                action_input = data.get("action_input")
                
                if not action or not action_input:
                    continue
                
                logger.info("ToolExecutionService: Executing tool '%s' with input: %s", action, action_input)
                
                result = await self._run_tool(action, action_input)
                if result:
                    tool_results.append({
                        "tool": action,
                        "query": action_input,
                        "result": result
                    })
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("ToolExecutionService: Failed to parse tool call: %s", str(e))
                continue
        
        return tool_results

    async def _run_tool(self, action: str, action_input: str) -> Any:
        """Dispatches to the specific service."""
        if action == "web_search":
            # 1. Search
            results = await search_service.search(action_input)
            # 2. Store in RAG for future context if needed
            if results:
                await rag_service.add_documents(results, action_input)
            return results
            
        elif action == "retrieve_documents":
            # Direct query to RAG
            return await rag_service.query(action_input)
            
        else:
            logger.warning("ToolExecutionService: Unknown action '%s'", action)
            return None

# Singleton instance
tool_execution_service = ToolExecutionService()
