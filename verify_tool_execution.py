import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.tool_execution_service import tool_execution_service

async def test_tool_execution():
    # Mock agent response with a tool call
    agent_output = """
    I need to find the latest results for the match.
    {
      "action": "web_search",
      "action_input": "India vs Pakistan Champions Trophy 2025 score"
    }
    """
    
    print("Testing Tool Execution Parser...")
    results = await tool_execution_service.execute_tools(agent_output)
    
    if not results:
        print("No tools executed.")
    else:
        for res in results:
            print(f"Executed Tool: {res['tool']}")
            print(f"Query: {res['query']}")
            # Since search might fail without key, we check if result is empty list or actual results
            print(f"Result Size: {len(res['result'])}")

if __name__ == "__main__":
    asyncio.run(test_tool_execution())
