"""Notion Toolbox sync — writes Tools to Notion database."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import httpx

from muse.models import NewsItem

NOTION_API_BASE = "https://api.notion.com/v1"


class NotionSync:
    """Sync Tools items to Notion Toolbox database."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        database_id: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("NOTION_API_KEY", "")
        self.database_id = database_id or os.environ.get("NOTION_TOOLBOX_DB_ID", "")
        self._client: Optional[httpx.AsyncClient] = None

    def _client_instance(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            }
            self._client = httpx.AsyncClient(
                base_url=NOTION_API_BASE,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    def is_configured(self) -> bool:
        return bool(self.api_key and self.database_id)

    async def create_tool_entry(self, item: NewsItem) -> bool:
        """Create a page in the Notion Toolbox database."""
        if not self.is_configured():
            return False
        
        client = self._client_instance()
        today = datetime.now().strftime("%Y-%m-%d")
        
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": item.title}}]},
                "URL": {"url": item.url},
                "Source": {"select": {"name": item.source}},
                "Status": {"select": {"name": "To Evaluate"}},
                "Added": {"date": {"start": today}},
            },
        }
        
        try:
            resp = await client.post("/pages", json=payload)
            return resp.status_code == 200
        except Exception:
            return False

    async def batch_sync(self, items: list[NewsItem]) -> int:
        """Sync multiple items. Returns count of successful syncs."""
        count = 0
        for item in items:
            if await self.create_tool_entry(item):
                count += 1
        return count

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
