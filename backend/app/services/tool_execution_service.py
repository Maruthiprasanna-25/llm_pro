"""
Tool execution service — interprets and executes agent-requested tool calls.
"""

from __future__ import annotations

import json
import logging
import re
from typing import List, Dict, Any

from app.services.search_service import search_service
from app.services.rag_service import rag_service
from app.services.sandbox_service import sandbox_service
from app.services.csv_parser_service import csv_parser_service
from app.services.security_service import security_service

logger = logging.getLogger(__name__)

class ToolExecutionService:
    """
    Orchestrates the execution of tools with enterprise-grade validation.
    """
    
    def __init__(self):
        # In a full enterprise implementation, these would be Pydantic models
        self.tool_registry = {
            "web_search": ["query"],
            "python_sandbox": ["code"],
            "csv_preview": ["filename"],
            "retrieve_documents": ["query"]
        }

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
                tool_name = data.get("tool_name")
                args = data.get("arguments", {})

                # Enterprise Schema Validation
                if action == "tool_call":
                    required_args = self.tool_registry.get(tool_name, [])
                    missing = [arg for arg in required_args if arg not in args]
                    if missing:
                        tool_results.append({
                            "status": "error", 
                            "message": f"Schema Violation: Missing required arguments for '{tool_name}': {', '.join(missing)}"
                        })
                        continue

                if action == "final_answer":
                    tool_results.append({"status": "final", "content": data.get("content", "")})
                    continue

                if action != "tool_call":
                    tool_results.append({"status": "error", "message": "Invalid action type."})
                    continue

                # 2. Whitelist & Security Validation
                if tool_name == "web_search":
                    query = args.get("query")
                    if not query:
                        tool_results.append({"status": "error", "message": "Missing search query."})
                        continue
                    
                    # Check for injection in query
                    if security_service.detect_injection(query):
                        tool_results.append({"status": "error", "message": "Security Alert: Search query contains restricted patterns."})
                        continue

                    results = await search_service.search(query)
                    # Store in RAG for later use
                    await rag_service.add_documents(results, query)
                    
                    # Mark as untrusted before returning to LLM
                    untrusted_data = "\n\n".join([f"Source: {r['url']}\n{r['content']}" for r in results])
                    tool_results.append({"status": "success", "output": security_service.mark_untrusted(untrusted_data)})

                elif tool_name == "python_sandbox":
                    code = args.get("code")
                    if not code:
                        tool_results.append({"status": "error", "message": "Missing python code."})
                        continue
                    
                    result = sandbox_service.execute_code(code)
                    tool_results.append({"status": "success", "output": json.dumps(result)})

                elif tool_name == "csv_preview":
                    filename = args.get("filename")
                    if not filename:
                        tool_results.append({"status": "error", "message": "Missing filename for CSV preview."})
                        continue
                    
                    result = csv_parser_service.get_preview(filename)
                    tool_results.append({"status": "success", "output": json.dumps(result)})

                elif tool_name == "retrieve_documents":
                    query = args.get("query")
                    if not query:
                        tool_results.append({"status": "error", "message": "Missing retrieval query."})
                        continue
                    
                    context = await rag_service.query(query)
                    tool_results.append({"status": "success", "output": security_service.mark_untrusted(context)})

                else:
                    tool_results.append({"status": "error", "message": f"Tool '{tool_name}' is not authorized."})

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("ToolExecutionService: Failed to parse tool call: %s", str(e))
                continue
            except Exception as e:
                logger.error(f"ToolExecution Error: {str(e)}")
                tool_results.append({"status": "error", "message": str(e)})
        
        return tool_results

# Singleton instance
tool_execution_service = ToolExecutionService()
