"""
Search service — official Brave Search API integration.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from app.core.config import get_settings
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

class SearchService:
    """
    Handles real-time web searches using the Brave Search API.
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.BRAVE_SEARCH_API_KEY
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.timeout = httpx.Timeout(20.0, connect=5.0)

    async def search(self, query: str, count: int = 5) -> list[dict[str, Any]]:
        """
        Execute a search query and return structured results.
        Returns a list of dicts with title, url, and snippet.
        """
        # Check Cache
        cache_key = cache_service.get_query_key(f"search_{query}")
        cached_result = cache_service.get(cache_key)
        if cached_result:
            logger.info("SearchService: Returning cached results for query: %s", query)
            return cached_result

        if not self.api_key:
            logger.warning("SearchService: BRAVE_SEARCH_API_KEY not set. Returning empty results.")
            return []

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        params = {
            "q": query,
            "count": count,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(self.base_url, headers=headers, params=params)
                resp.raise_for_status()
                data = resp.json()

                results = []
                # Brave returns web results in data['web']['results']
                web_results = data.get("web", {}).get("results", [])
                for res in web_results:
                    results.append({
                        "title": res.get("title"),
                        "url": res.get("url"),
                        "snippet": res.get("description"), # Brave uses 'description' as snippet
                        "source": "Brave Search"
                    })
                
                logger.info("SearchService: Successfully retrieved %d results for query: %s", len(results), query)
                
                # Store in Cache
                cache_service.set(cache_key, results)
                return results

        except httpx.HTTPStatusError as e:
            logger.error("SearchService: HTTP error %d: %s", e.response.status_code, e.response.text)
            return []
        except Exception as e:
            logger.error("SearchService: Unexpected error during search: %s", str(e))
            return []

# Singleton instance
search_service = SearchService()
