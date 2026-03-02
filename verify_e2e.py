import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.agent_orchestrator import orchestrator

async def test_e2e_rag_system():
    # A query that should trigger ResearchAgent -> Tools -> Synthesis
    query = "Research the current status of the ICC Champions Trophy 2025 and provide key highlights."
    
    # Mocking the plan that PlannerAgent would generate
    mock_plan = {
        "type": "TASK_PLAN",
        "goal_summary": "ICC Champions Trophy 2025 Research",
        "tasks": [
            {
                "agent": "research",
                "description": "Find the latest news and hosting status of ICC Champions Trophy 2025."
            }
        ]
    }
    
    print("--- STARTING E2E VERIFICATION ---")
    print(f"Goal: {query}")
    
    try:
        final_report = await orchestrator.execute_plan(mock_plan)
        print("\n--- FINAL SYSTEM OUTPUT ---")
        print(final_report)
        print("\n--- E2E VERIFICATION COMPLETE ---")
    except Exception as e:
        print(f"E2E Verification Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_e2e_rag_system())
