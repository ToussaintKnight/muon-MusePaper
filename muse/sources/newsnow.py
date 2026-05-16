"""NewsNow API client — Chinese platform aggregator."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Optional

import httpx

from muse.models import NewsItem
from muse.sources.base import SourceClient

DEFAULT_SOURCE_IDS = [
    "weibo", "baidu", "zhihu", "bilibili",
    "36kr", "sspai", "v2ex", "juejin",
    "wallstreetcn", "thepaper", "toutiao",
    "ithome", "coolapk", "solidot",
]

NEWSNOW_API = "https://newsnow.busiyi.world/api/s"


class NewsNowClient(SourceClient):
    """Fetch trending content from NewsNow's 44 Chinese sources."""

    source_type = "newsnow"

    def __init__(
        self,
        source_ids: Optional[list[str]] = None,
        api_base: str = NEWSNOW_API,
        timeout: float = 10.0,
    ):
        self.source_ids = source_ids or DEFAULT_SOURCE_IDS
        self.api_base = api_base
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _client_instance(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def fetch(self) -> list[NewsItem]:
        """Fetch all configured sources."""
        items: list[NewsItem] = []
        for sid in self.source_ids:
            try:
                source_items = await self._fetch_source(sid)
                items.extend(source_items)
            except Exception:
                # Individual source failure is non-fatal
                continue
        return items

    async def _fetch_source(self, source_id: str) -> list[NewsItem]:
        client = self._client_instance()
        url = f"{self.api_base}?id={source_id}"
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

        raw_items = data.get("items", []) if isinstance(data, dict) else data
        results: list[NewsItem] = []
        for idx, it in enumerate(raw_items[:30]):  # cap at 30 per source
            item_id = hashlib.md5(
                f"newsnow:{source_id}:{it.get('title','')}".encode()
            ).hexdigest()[:12]
            results.append(
                NewsItem(
                    id=item_id,
                    title=it.get("title", "").strip(),
                    url=it.get("url", ""),
                    source=f"newsnow_{source_id}",
                    source_type="newsnow",
                    pub_date=_parse_date(it.get("pubDate")),
                    extra={
                        "newsnow_source": source_id,
                        "mobile_url": it.get("mobileUrl"),
                    },
                )
            )
        return results

    async def health_check(self) -> bool:
        try:
            client = self._client_instance()
            resp = await client.get(f"{self.api_base}?id=weibo")
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None


def _parse_date(ds: Optional[str]) -> Optional[datetime]:
    if not ds:
        return None
    try:
        # NewsNow returns ISO format
        return datetime.fromisoformat(ds.replace("Z", "+00:00"))
    except Exception:
        return None
