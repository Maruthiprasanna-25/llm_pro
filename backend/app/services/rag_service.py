"""
RAG service — ChromaDB integration for vector storage and retrieval.
"""

from __future__ import annotations

import logging
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class RAGService:
    """
    Handles document embedding, storage, and similarity search via ChromaDB.
    """

    def __init__(self):
        self.db_path = get_settings().CHROMA_DB_PATH
        self.client = None
        self.collection = None
        self.is_active = False

        try:
            import chromadb
            # Attempt initialization - this might panic on some Windows systems
            self.client = chromadb.PersistentClient(path=self.db_path)
            self.collection = self.client.get_or_create_collection(name="web_search_cache")
            self.is_active = True
            logger.info("RAGService: ChromaDB initialized successfully.")
        except (Exception, BaseException) as e:
            logger.error(f"RAGService: Failed to initialize ChromaDB (graceful fallback): {str(e)}")
            # Even if it panics, we've caught it if it's a Python-level PanicException

    async def add_documents(self, results: list[dict[str, Any]], query: str):
        """
        Store search results in the vector database.
        Each document should have 'title', 'url', and 'snippet'.
        """
        if not self.is_active:
            logger.warning("RAGService: Skipping document insertion (ChromaDB inactive).")
            return

        if not results:
            return

        ids = []
        metadatas = []
        texts = []

        for i, doc in enumerate(results):
            # Unique ID for each snippet
            doc_id = f"{query.replace(' ', '_')}_{i}"
            ids.append(doc_id)
            metadatas.append({
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "query": query
            })
            texts.append(doc.get("snippet", ""))

        try:
            # Chroma handles embedding internally if not provided (default: all-MiniLM-L6-v2)
            self.collection.add(
                ids=ids,
                metadatas=metadatas,
                documents=texts
            )
            logger.info("RAGService: Added %d documents to collection", len(results))
        except Exception as e:
            logger.error("RAGService: Error adding documents: %s", str(e))

    async def query(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant context for a query.
        """
        if not self.is_active:
            logger.warning("RAGService: Skipping query (ChromaDB inactive).")
            return ""

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # results['documents'] is a list of lists
            snippets = results.get("documents", [[]])[0]
            context = "\n\n".join(snippets)
            
            logger.info("RAGService: Retrieved %d context chunks for query: %s", len(snippets), query_text)
            return context
        except Exception as e:
            logger.error("RAGService: Error querying vector DB: %s", str(e))
            return ""

# Singleton instance
rag_service = RAGService()
