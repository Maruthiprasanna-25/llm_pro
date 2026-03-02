import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.tech_service import perform_tech_task

async def test_tech(task: str):
    print(f"\n--- Testing Tech Task: '{task}' ---")
    result = await perform_tech_task(task)
    print("Agent Response:")
    print("-" * 30)
    print(result)
    print("-" * 30)

async def main():
    task = "Write a Python function to calculate the Fibonacci sequence up to N terms using recursion with memoization."
    await test_tech(task)

if __name__ == "__main__":
    asyncio.run(main())
