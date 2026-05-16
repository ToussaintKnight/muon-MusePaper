"""Native API clients — zero-auth APIs (Reddit, Hacker News)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

import httpx

from muse.models import NewsItem
from muse.sources.base import SourceClient


class NativeAPIClient(SourceClient):
    """Fetch from free, no-auth APIs."""

    source_type = "native"

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _client_instance(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def fetch(self) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            items.extend(await self._fetch_reddit("technology"))
        except Exception:
            pass
        try:
            items.extend(await self._fetch_hackernews())
        except Exception:
            pass
        return items

    async def _fetch_reddit(self, subreddit: str) -> list[NewsItem]:
        client = self._client_instance()
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
        resp = await client.get(url, headers={"User-Agent": "Muse/2.0"})
        resp.raise_for_status()
        data = resp.json()

        results: list[NewsItem] = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            title = post.get("title", "").strip()
            if not title:
                continue
            item_id = hashlib.md5(
                f"reddit:{subreddit}:{title}".encode()
            ).hexdigest()[:12]
            created_utc = post.get("created_utc")
            pub_date = (
                datetime.fromtimestamp(created_utc, tz=timezone.utc)
                if created_utc else None
            )
            results.append(
                NewsItem(
                    id=item_id,
                    title=title,
                    url=f"https://reddit.com{post.get('permalink', '')}",
                    source=f"reddit_{subreddit}",
                    source_type="native",
                    pub_date=pub_date,
                    heat_score=post.get("score"),
                    extra={"subreddit": subreddit, "comments": post.get("num_comments")},
                )
            )
        return results

    async def _fetch_hackernews(self) -> list[NewsItem]:
        client = self._client_instance()
        # Get top story IDs
        resp = await client.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json"
        )
        resp.raise_for_status()
        story_ids = resp.json()[:20]

        results: list[NewsItem] = []
        for sid in story_ids:
            try:
                item_resp = await client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                )
                item_resp.raise_for_status()
                story = item_resp.json()
                if not story or story.get("type") != "story":
                    continue
                title = story.get("title", "").strip()
                if not title:
                    continue
                item_id = f"hn_{sid}"
                created = story.get("time")
                pub_date = (
                    datetime.fromtimestamp(created, tz=timezone.utc)
                    if created else None
                )
                results.append(
                    NewsItem(
                        id=item_id,
                        title=title,
                        url=story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        source="hackernews",
                        source_type="native",
                        pub_date=pub_date,
                        heat_score=story.get("score"),
                        extra={"comments": story.get("descendants", 0)},
                    )
                )
            except Exception:
                continue
        return results

    async def health_check(self) -> bool:
        try:
            client = self._client_instance()
            resp = await client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
