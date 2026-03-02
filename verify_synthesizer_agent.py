import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.synthesizer_service import perform_synthesis

async def test_synthesizer(outputs: list[dict[str, str]]):
    print(f"\n--- Testing Synthesizer Agent ---")
    result = await perform_synthesis(outputs)
    print("Agent Response:")
    print("-" * 30)
    print(result)
    print("-" * 30)

async def main():
    outputs = [
        {
            "agent": "ResearchAgent",
            "content": "RESEARCH SUMMARY:\nKey Findings:\n- Users want faster response times.\n- Mobile support is critical."
        },
        {
            "agent": "AnalystAgent",
            "content": "ANALYSIS REPORT:\n- Feasibility: High.\n- Risks: Server scalability."
        },
        {
            "agent": "TechAgent",
            "content": "CODE IMPLEMENTATION REPORT:\nProblem Understanding:\n- Faster API layer required.\nTechnical Approach:\n- Implement GraphQL for efficiency."
        }
    ]
    await test_synthesizer(outputs)

if __name__ == "__main__":
    asyncio.run(main())
