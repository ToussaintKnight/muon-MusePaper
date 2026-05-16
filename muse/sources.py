"""Camofox-based source crawlers for international sites.

Each source is an async function that:
  1. Creates a Camofox tab navigating to the URL
  2. Gets the accessibility tree snapshot
  3. Parses it into NewsItem[]
  4. Closes the tab
  5. Returns items

This mirrors NewsNow's ``defineSource(async () => { ... })`` pattern.
NewsNow uses myFetch + cheerio; we use Camofox + accessibility tree parser.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from muse.camofox import get_client, check_available
from muse.parsers import get_parser
from muse.types import NewsItem, SourceDef

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Source definitions — mirrors NewsNow's pre-sources.ts
# ---------------------------------------------------------------------------

SOURCES: dict[str, SourceDef] = {
    "hackernews": SourceDef(
        id="hackernews",
        name="Hacker News",
        url="https://news.ycombinator.com/",
        interval=300,        # 5 min — HN updates constantly
        category="global",
        parser_hint="hackernews",
        home="https://news.ycombinator.com/",
        max_items=30,
    ),
    "github-trending": SourceDef(
        id="github-trending",
        name="GitHub Trending",
        url="https://github.com/trending",
        interval=3600,       # 1 hour — daily cadence
        category="global",
        parser_hint="github-trending",
        home="https://github.com/trending",
        max_items=25,
    ),
    "producthunt": SourceDef(
        id="producthunt",
        name="Product Hunt",
        url="https://www.producthunt.com/",
        interval=3600,       # 1 hour
        category="global",
        parser_hint="producthunt",
        home="https://www.producthunt.com/",
        max_items=20,
    ),
    "techcrunch": SourceDef(
        id="techcrunch",
        name="TechCrunch",
        url="https://techcrunch.com/",
        interval=1800,       # 30 min
        category="global",
        parser_hint="techcrunch",
        home="https://techcrunch.com/",
        max_items=20,
    ),
    "reddit": SourceDef(
        id="reddit",
        name="Reddit (Top Today)",
        url="https://www.reddit.com/r/all/top/?t=day",
        interval=3600,       # 1 hour
        category="global",
        parser_hint="reddit",
        home="https://www.reddit.com/r/all/top/?t=day",
        max_items=25,
    ),
}


def list_sources(category: Optional[str] = None) -> list[SourceDef]:
    """List all enabled sources, optionally filtered by category."""
    return [
        s for s in SOURCES.values()
        if s.enabled and (category is None or s.category == category)
    ]


# ---------------------------------------------------------------------------
# Crawl a single source (Camofox-based)
# ---------------------------------------------------------------------------

async def crawl_source(source_id: str) -> list[NewsItem]:
    """Crawl one source by ID. Returns NewsItem[]. Raises on failure."""
    source = SOURCES.get(source_id)
    if not source:
        raise ValueError(f"Unknown source: {source_id}. Available: {list(SOURCES.keys())}")
    if not source.url:
        raise ValueError(f"Source {source_id} has no URL configured")

    if not check_available():
        raise RuntimeError("Camofox browser not available at http://localhost:9377")

    parser = get_parser(source.parser_hint)
    client = get_client()

    logger.info(f"[crawl] {source_id}: opening {source.url}")
    tab = client.crawl_page(source.url, wait=5)
    try:
        snapshot = tab.snapshot()
        items = parser(snapshot)
        logger.info(f"[crawl] {source_id}: parsed {len(items)} items")

        # Cap and tag
        items = items[:source.max_items]
        for item in items:
            item.source = source_id

        return items
    except Exception as e:
        logger.error(f"[crawl] {source_id}: failed: {e}")
        raise
    finally:
        tab.close()


# ---------------------------------------------------------------------------
# Batch crawl — run multiple sources, aggregate results
# ---------------------------------------------------------------------------

async def crawl_all(source_ids: Optional[list[str]] = None,
                    category: Optional[str] = None) -> dict[str, list[NewsItem]]:
    """Crawl multiple sources. Returns {source_id: [NewsItem, ...]}.

    If *source_ids* is None, all enabled sources are crawled.
    If *category* is set, only sources in that category are crawled.
    """
    if source_ids:
        targets = [SOURCES[sid] for sid in source_ids if sid in SOURCES]
    else:
        targets = list_sources(category)

    if not targets:
        return {}

    results: dict[str, list[NewsItem]] = {}
    for source in targets:
        try:
            results[source.id] = await crawl_source(source.id)
        except Exception as e:
            logger.error(f"[crawl] {source.id}: failed: {e}")
            results[source.id] = []

    return results
