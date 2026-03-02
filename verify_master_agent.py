import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.master_service import analyze_request

async def test_analysis(goal: str):
    print(f"\n--- Testing: '{goal}' ---")
    result = await analyze_request(goal)
    print(f"Decision: {result['decision']}")
    print(f"Recommended Mode: {result['recommended_mode']}")
    print(f"Reasoning: {result['reasoning']}")
    
    # Verify Fast Filter for short queries
    words = goal.strip().split()
    if len(words) <= 6:
        if result['reasoning'] == "Short query detected.":
            print("✅ Fast Filter works as expected.")
        else:
            print("❌ Fast Filter failed.")
    else:
        print("ℹ️ Semantic (LLM) classification performed.")

async def main():
    goals = [
        "Hi", # Short query
        "What is an LLM?", # Short query
        "Give me a 30-day implementation roadmap to master LLM systems engineering.", # Complex semantic
        "I need a detailed strategy for my project research analysis on AI impact.", # Complex semantic
        "Can you explain the difference between REST and GraphQL in simple terms?", # Simple semantic (likely)
    ]
    
    for goal in goals:
        await test_analysis(goal)

if __name__ == "__main__":
    asyncio.run(main())
