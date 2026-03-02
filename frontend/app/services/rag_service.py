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
        settings = get_settings()
        self.db_path = settings.CHROMA_DB_PATH
        self.client = chromadb.PersistentClient(path=self.db_path)
        # Collection for web search results
        self.collection = self.client.get_or_create_collection(name="web_search_cache")

    async def add_documents(self, documents: list[dict[str, Any]], query_context: str):
        """
        Store search results in the vector database.
        Each document should have 'title', 'url', and 'snippet'.
        """
        if not documents:
            return

        ids = []
        metadatas = []
        texts = []

        for i, doc in enumerate(documents):
            # Unique ID for each snippet
            doc_id = f"{query_context.replace(' ', '_')}_{i}"
            ids.append(doc_id)
            metadatas.append({
                "title": doc.get("title", ""),
                "url": doc.get("url", ""),
                "query": query_context
            })
            texts.append(doc.get("snippet", ""))

        try:
            # Chroma handles embedding internally if not provided (default: all-MiniLM-L6-v2)
            self.collection.add(
                ids=ids,
                metadatas=metadatas,
                documents=texts
            )
            logger.info("RAGService: Added %d documents to collection", len(documents))
        except Exception as e:
            logger.error("RAGService: Error adding documents: %s", str(e))

    async def query(self, query_text: str, n_results: int = 3) -> str:
        """
        Perform a similarity search and return a concatenated context string.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
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
