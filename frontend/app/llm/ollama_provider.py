"""
Ollama LLM provider — calls the local Ollama HTTP API.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from app.core.config import get_settings
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are Campus AI, an intelligent assistant for educational institutions. "
    "Provide structured, clear, and professional responses. "
    "Use headings and bullet points when appropriate."
)


class OllamaProvider(LLMProvider):
    """Talks to a local Ollama instance via its REST API."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = httpx.Timeout(300.0, connect=10.0)

    def _prepare_messages(self, messages: list[dict]) -> list[dict]:
        """Prepend system prompt if not already present."""
        if not messages or messages[0].get("role") != "system":
            return [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        return messages

    async def generate(self, messages: list[dict], **kwargs) -> str:
        """Full (non-streaming) response."""
        # Extract timeout if provided, else use default
        request_timeout = kwargs.pop("request_timeout", self.timeout)
        if isinstance(request_timeout, (int, float)):
            request_timeout = httpx.Timeout(float(request_timeout), connect=10.0)

        options = {"temperature": 0.6}
        options.update(kwargs)

        prepared = self._prepare_messages(messages)
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": prepared,
                    "stream": False,
                    "options": options,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]

    async def stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        """Stream tokens from Ollama's /api/chat endpoint."""
        # Extract timeout if provided, else use default
        request_timeout = kwargs.pop("request_timeout", self.timeout)
        if isinstance(request_timeout, (int, float)):
            request_timeout = httpx.Timeout(float(request_timeout), connect=10.0)

        options = {"temperature": 0.6}
        options.update(kwargs)

        prepared = self._prepare_messages(messages)
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": prepared,
                    "stream": True,
                    "options": options,
                },
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                    except json.JSONDecodeError:
                        logger.warning("Non-JSON line from Ollama: %s", line)
