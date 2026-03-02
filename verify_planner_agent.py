import asyncio
import sys
import os
import json

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.planner_service import generate_plan

async def test_planning(goal: str):
    print(f"\n--- Testing goal: '{goal}' ---")
    result = await generate_plan(goal)
    print(f"Plan Type: {result.get('type')}")
    
    if result.get("type") == "TASK_PLAN":
        print(f"Goal Summary: {result.get('goal_summary')}")
        print("Tasks:")
        for task in result.get("tasks", []):
            print(f"  Step {task['step']} [{task['agent']}]: {task['task']}")
    elif result.get("type") == "CLARIFICATION_REQUIRED":
        print(f"Clarification Question: {result.get('question')}")
    
    # Basic Validation
    if result.get("type") not in ["TASK_PLAN", "CLARIFICATION_REQUIRED"]:
        print("❌ Invalid result type.")
    else:
        print("✅ Result structure is valid.")

async def main():
    goals = [
        "Give me a 30-day implementation roadmap to master LLM systems engineering.",
        "Design a high-level system architecture for a campus management app including database and security strategy.",
        "Help me improve my project.", # Should trigger clarification
        "Analyze the current market trends in AI and provide a competitive strategy for a new startup."
    ]
    
    for goal in goals:
        await test_planning(goal)

if __name__ == "__main__":
    asyncio.run(main())
