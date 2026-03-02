import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.research_service import perform_research

async def test_research(task: str):
    print(f"\n--- Testing Research Task: '{task}' ---")
    result = await perform_research(task)
    print("Agent Response:")
    print("-" * 30)
    print(result)
    print("-" * 30)

async def main():
    tasks = [
        "What is the capital of France?", # Simple, direct
        "Analyze the current market trends for generative AI in 2024.", # Complex, should trigger tool call or research summary
        "Do we have any internal reports on the Campus AI system architecture?", # Internal, should trigger retrieve_documents
    ]
    
    for task in tasks:
        await test_research(task)

if __name__ == "__main__":
    asyncio.run(main())
