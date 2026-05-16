"""Source aggregator — merges, deduplicates, normalizes content from all sources."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Optional

from muse.models import NewsItem
from muse.sources.base import SourceClient


class SourceAggregator:
    """Merges all source clients, deduplicates, normalizes."""

    def __init__(self, clients: list[SourceClient], similarity_threshold: float = 0.82):
        self.clients = clients
        self.similarity_threshold = similarity_threshold

    async def fetch_all(self) -> list[NewsItem]:
        """Fetch from all sources and merge."""
        all_items: list[NewsItem] = []
        for client in self.clients:
            try:
                items = await client.fetch()
                all_items.extend(items)
            except Exception:
                continue
        return self.deduplicate(all_items)

    def deduplicate(self, items: list[NewsItem]) -> list[NewsItem]:
        """Remove near-duplicate titles using fuzzy matching."""
        unique: list[NewsItem] = []
        for item in items:
            if not item.title:
                continue
            is_duplicate = False
            for existing in unique:
                if _title_similarity(item.title, existing.title) >= self.similarity_threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique.append(item)
        return unique

    async def health_check(self) -> dict[str, bool]:
        """Check health of all sources."""
        results: dict[str, bool] = {}
        for client in self.clients:
            try:
                results[client.source_type] = await client.health_check()
            except Exception:
                results[client.source_type] = False
        return results

    async def close_all(self) -> None:
        """Close all client connections."""
        for client in self.clients:
            if hasattr(client, "close"):
                await client.close()


def _title_similarity(a: str, b: str) -> float:
    """Fuzzy title similarity."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
