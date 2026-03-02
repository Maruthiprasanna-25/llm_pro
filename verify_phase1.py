import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.services.search_service import search_service
from app.services.rag_service import rag_service

async def test_phase1():
    query = "latest news on ICC champions trophy 2025"
    print(f"Testing Search with query: {query}")
    
    # 1. Test Search
    results = await search_service.search(query)
    if not results:
        print("Search failed (likely missing API key). Testing RAG with mock data.")
        results = [
            {"title": "Mock Result 1", "url": "http://mock1.com", "snippet": "ICC Champions Trophy 2025 will be held in Pakistan."},
            {"title": "Mock Result 2", "url": "http://mock2.com", "snippet": "The tournament features top 8 ODI teams."}
        ]
    else:
        print(f"Found {len(results)} results.")
    
    # 2. Test RAG Storage
    print("\nTesting RAG Storage...")
    await rag_service.add_documents(results, query)
    
    print("\nTesting RAG Retrieval...")
    context = await rag_service.query("Champions Trophy host")
    print(f"Retrieved Context:\n{context}")

if __name__ == "__main__":
    asyncio.run(test_phase1())
