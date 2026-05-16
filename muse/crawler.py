"""Caching crawler — NewsNow-style interval + TTL cache layer.

NewsNow's cache pattern:
  - interval: per-source refresh interval (how often to actually re-scrape)
  - TTL: global cache lifetime (10 min)
  - If now - cache.updated < interval → return cache directly
  - If now - cache.updated < TTL → return cache (even if stale)
  - If now - cache.updated > TTL → return cache but trigger background refresh
  - If now - cache.updated > TTL + 2*interval → force refresh synchronously

We replicate this exactly, using local JSON files as cache backend
(fits single-user, no D1 needed).
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from muse.sources import SOURCES, crawl_source, crawl_all, list_sources
from muse.types import NewsItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_CACHE_DIR = Path("/Volumes/Lab/muon-muse/data/cache")
DEFAULT_TTL = 600  # 10 minutes — NewsNow default TTL
FORCE_REFRESH_MULTIPLIER = 2  # if cache age > TTL + interval*2 → force sync

# ---------------------------------------------------------------------------
# Cache entry
# ---------------------------------------------------------------------------

class CacheEntry:
    def __init__(self, source_id: str, items: list[NewsItem], updated: float):
        self.source_id = source_id
        self.items = items
        self.updated = updated  # epoch seconds

    @property
    def age(self) -> float:
        return time.time() - self.updated

    @property
    def is_stale(self) -> bool:
        """True if cache is beyond TTL and needs refresh."""
        return self.age > DEFAULT_TTL

    @property
    def needs_force_refresh(self) -> bool:
        """True if cache is so old we should block and refresh."""
        source = SOURCES.get(self.source_id)
        interval = source.interval if source else 600
        return self.age > (DEFAULT_TTL + interval * FORCE_REFRESH_MULTIPLIER)

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "updated": self.updated,
            "items": [item.to_dict() for item in self.items],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CacheEntry":
        items = [NewsItem(**item) for item in d.get("items", [])]
        return cls(d["source_id"], items, d.get("updated", 0))


# ---------------------------------------------------------------------------
# Cache backend — local JSON files (single-user, no DB)
# ---------------------------------------------------------------------------

class LocalCache:
    """File-based cache, one JSON file per source.

    Single user, ~6 sources × 30 items × ~500 bytes = ~90KB total.
    No database needed — same philosophy as Muse's no-vector-DB decision.
    """

    def __init__(self, cache_dir: str | Path = DEFAULT_CACHE_DIR):
        self._dir = Path(cache_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, source_id: str) -> Path:
        return self._dir / f"{source_id}.json"

    def get(self, source_id: str) -> Optional[CacheEntry]:
        path = self._path(source_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return CacheEntry.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"[cache] corrupt file for {source_id}: {e}")
            return None

    def set(self, source_id: str, items: list[NewsItem]) -> None:
        entry = CacheEntry(source_id, items, time.time())
        self._path(source_id).write_text(
            json.dumps(entry.to_dict(), ensure_ascii=False, indent=2)
        )
        logger.info(f"[cache] saved {len(items)} items for {source_id}")

    def get_all(self, source_ids: Optional[list[str]] = None) -> dict[str, CacheEntry]:
        if source_ids is None:
            source_ids = list(SOURCES.keys())
        result = {}
        for sid in source_ids:
            entry = self.get(sid)
            if entry:
                result[sid] = entry
        return result


# ---------------------------------------------------------------------------
# Cache + crawl orchestrator (NewsNow's api/s/index.ts pattern)
# ---------------------------------------------------------------------------

_cache: Optional[LocalCache] = None


def get_cache() -> LocalCache:
    global _cache
    if _cache is None:
        _cache = LocalCache()
    return _cache


def get_cached(source_id: str) -> Optional[list[NewsItem]]:
    """Get cached items for a source, or None if never cached."""
    entry = get_cache().get(source_id)
    if entry:
        return entry.items
    return None


async def fetch_source(source_id: str) -> list[NewsItem]:
    """Fetch a source with caching — NewsNow pattern.

    1. Check cache
    2. If cache is fresh (age < interval) → return cache
    3. If cache is stale but not expired (age < TTL) → return cache (lazy refresh)
    4. If cache is expired → crawl synchronously
    5. If no cache → crawl synchronously
    """
    source = SOURCES.get(source_id)
    if not source:
        raise ValueError(f"Unknown source: {source_id}")

    cache = get_cache()
    entry = cache.get(source_id)

    if entry:
        # Step 2: Cache is fresh (age < interval) — return immediately
        if entry.age < source.interval:
            logger.debug(f"[fetch] {source_id}: fresh cache ({entry.age:.0f}s < {source.interval}s)")
            return entry.items

        # Step 3: Cache is stale but within TTL — return cache, refresh in background
        if not entry.needs_force_refresh:
            logger.info(f"[fetch] {source_id}: stale cache ({entry.age:.0f}s), refreshing in background")
            # In a real async system, spawn background task here
            # For now, just refresh inline (single-threaded is fine for single user)
            try:
                items = await crawl_source(source_id)
                cache.set(source_id, items)
                return items
            except Exception as e:
                logger.warning(f"[fetch] {source_id}: background refresh failed: {e}")
                return entry.items  # Return stale cache as fallback

        # Step 4: Cache is very old — force refresh
        logger.info(f"[fetch] {source_id}: cache expired ({entry.age:.0f}s > TTL), forcing refresh")
        items = await crawl_source(source_id)
        cache.set(source_id, items)
        return items

    # Step 5: No cache — crawl from scratch
    logger.info(f"[fetch] {source_id}: no cache, crawling")
    items = await crawl_source(source_id)
    cache.set(source_id, items)
    return items


async def fetch_all(sources: Optional[list[str]] = None) -> dict[str, list[NewsItem]]:
    """Fetch all sources with caching."""
    if sources is None:
        sources = [s.id for s in list_sources()]

    results: dict[str, list[NewsItem]] = {}
    for sid in sources:
        try:
            results[sid] = await fetch_source(sid)
        except Exception as e:
            logger.error(f"[fetch] {sid}: failed: {e}")
            results[sid] = get_cached(sid) or []

    return results


def clear_cache(source_id: Optional[str] = None) -> None:
    """Clear cache for one or all sources."""
    cache = get_cache()
    if source_id:
        path = cache._path(source_id)
        if path.exists():
            path.unlink()
        logger.info(f"[cache] cleared {source_id}")
    else:
        import shutil
        shutil.rmtree(cache._dir, ignore_errors=True)
        cache._dir.mkdir(parents=True, exist_ok=True)
        logger.info("[cache] cleared all")
