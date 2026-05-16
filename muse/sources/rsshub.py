"""RSSHub client — International platform aggregator."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Optional

import httpx

from muse.models import NewsItem
from muse.sources.base import SourceClient

DEFAULT_ROUTES = [
    "hackernews",
    "github/trending/daily",
    "producthunt/today",
    "techcrunch/news",
]

RSSHub_BASE = "http://localhost:1200"


class RSSHubClient(SourceClient):
    """Fetch content from self-hosted RSSHub instance."""

    source_type = "rsshub"

    def __init__(
        self,
        routes: Optional[list[str]] = None,
        base_url: str = RSSHub_BASE,
        timeout: float = 15.0,
    ):
        self.routes = routes or DEFAULT_ROUTES
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _client_instance(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
            self._client = httpx.AsyncClient(timeout=self.timeout, headers=headers)
        return self._client

    async def fetch(self) -> list[NewsItem]:
        items: list[NewsItem] = []
        for route in self.routes:
            try:
                route_items = await self._fetch_route(route)
                items.extend(route_items)
            except Exception:
                continue
        return items

    async def _fetch_route(self, route: str) -> list[NewsItem]:
        client = self._client_instance()
        url = f"{self.base_url}/{route}"
        resp = await client.get(url, headers={"Accept": "application/json"})
        resp.raise_for_status()
        data = resp.json()

        feed_items = data.get("item", []) if isinstance(data, dict) else []
        if not feed_items and isinstance(data, dict):
            feed_items = data.get("items", [])

        results: list[NewsItem] = []
        for idx, it in enumerate(feed_items[:25]):
            title = it.get("title", "").strip()
            if not title:
                continue
            item_id = hashlib.md5(
                f"rsshub:{route}:{title}".encode()
            ).hexdigest()[:12]
            results.append(
                NewsItem(
                    id=item_id,
                    title=title,
                    url=it.get("link", ""),
                    source=f"rsshub_{route.replace('/', '_')}",
                    source_type="rsshub",
                    pub_date=_parse_rss_date(it.get("pubDate")),
                    extra={"rsshub_route": route},
                )
            )
        return results

    async def health_check(self) -> bool:
        try:
            client = self._client_instance()
            resp = await client.get(f"{self.base_url}/hackernews")
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


def _parse_rss_date(ds: Optional[str]) -> Optional[datetime]:
    if not ds:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",   # RFC 822
        "%Y-%m-%dT%H:%M:%S%z",         # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",          # ISO 8601 UTC
        "%Y-%m-%d %H:%M:%S",           # Simple
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ds, fmt)
        except ValueError:
            continue
    return None
