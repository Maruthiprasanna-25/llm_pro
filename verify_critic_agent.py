import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.critic_service import perform_review

async def test_critic(content: str):
    print(f"\n--- Testing Critic Review on content snippet ---")
    result = await perform_review(content)
    print("Agent Response:")
    print("-" * 30)
    print(result)
    print("-" * 30)

async def main():
    content = """
    Plan for Mars Colony:
    1. Send 100 people without water or food.
    2. Hope they find underground rivers.
    3. If they don't, send a second mission with sandwiches.
    """
    await test_critic(content)

if __name__ == "__main__":
    asyncio.run(main())
