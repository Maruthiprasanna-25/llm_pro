import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.analyst_service import perform_analysis

async def test_analysis(task: str):
    print(f"\n--- Testing Analyst Task: '{task}' ---")
    result = await perform_analysis(task)
    print("Agent Response:")
    print("-" * 30)
    print(result)
    print("-" * 30)

async def main():
    tasks = [
        "Evaluate the feasibility of building a Mars colony in the next 10 years.",
        "Analyze the risks and timeline for migrating a legacy monolithic application to microservices.",
        "Perform a SWOT analysis for a new AI-powered campus management platform.",
    ]
    
    for task in tasks:
        await test_analysis(task)

if __name__ == "__main__":
    asyncio.run(main())
