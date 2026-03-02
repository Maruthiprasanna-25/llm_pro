"""
Cache service — simple SQLite persistent cache for search results and queries.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
from typing import Any, Optional

logger = logging.getLogger(__name__)

class CacheService:
    """
    Persistent key-value cache using SQLite.
    """

    def __init__(self, db_path: str = "./app_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at REAL
                )
            """)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache if not expired."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    value_json, expires_at = row
                    if expires_at > time.time():
                        return json.loads(value_json)
                    else:
                        # Expired
                        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        except Exception as e:
            logger.error("CacheService: Error getting key %s: %s", key, str(e))
        return None

    def set(self, key: str, value: Any, ttl: int = 86400):
        """Store a value in the cache with a Time-To-Live (seconds)."""
        try:
            expires_at = time.time() + ttl
            value_json = json.dumps(value)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                    (key, value_json, expires_at)
                )
        except Exception as e:
            logger.error("CacheService: Error setting key %s: %s", key, str(e))

    def get_query_key(self, query: str) -> str:
        """Generate a stable cache key for a query string."""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

# Singleton instance
cache_service = CacheService()
