"""
Tavily Search Service — Official API integration for AI-optimized web search.
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
from app.services.security_service import security_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

class TavilySearchService:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"

    async def search(self, query: str, search_depth: str = "basic") -> List[Dict[str, Any]]:
        """
        Executes a search using Tavily API.
        Returns a list of sanitized results.
        """
        if not self.api_key:
            logger.warning("TavilySearchService: TAVILY_API_KEY not set. Using mock results.")
            return []

        # Check Cache
        cache_key = cache_service.get_query_key(f"tavily_{query}_{search_depth}")
        cached = cache_service.get(cache_key)
        if cached:
            return cached

        # Validate query length (Security Rule)
        if len(query) > 300:
            query = query[:300]

        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": False,
            "include_raw_content": False,
            "max_results": 5
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    # Sanitize content (Security Rule)
                    clean_content = security_service.sanitize_web_content(item.get("content", ""))
                    results.append({
                        "title": item.get("title", "No Title"),
                        "url": item.get("url", ""),
                        "content": clean_content
                    })

                cache_service.set(cache_key, results)
                return results

        except Exception as e:
            logger.error(f"TavilySearchService Error: {str(e)}")
            return []

search_service = TavilySearchService()
