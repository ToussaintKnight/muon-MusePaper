"""Muse Engine — dual-source crawler orchestrator with vector ranking.

Combines:
  - Source A (China): NewsNow API — 44 Chinese platform hot lists
  - Source B (Global): Camofox browser — international sites (HN, GH, PH, etc.)
  - Vector ranking: bge-small-zh-v1.5 → cosine with interest vector

Daily routine:
  1. Fetch all sources (cached via NewsNow-style interval/TTL)
  2. Embed all item titles with bge-small-zh (256-dim)
  3. Cosine rank against user interest vector
  4. Return top 50 items
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional, Any

from muse.crawler import fetch_source, get_cache, SOURCES as CAMOFOX_SOURCES
from muse.newsnow import fetch_newsnow_source, NEWSNOW_SOURCES
from muse.types import NewsItem, SourceDef

logger = logging.getLogger(__name__)


async def fetch_all_unified(source_filter: Optional[list[str]] = None) -> list[NewsItem]:
    """Fetch ALL sources (NewsNow + Camofox) and return unified list."""
    all_items: list[NewsItem] = []

    # Phase 1: Camofox sources (international)
    if source_filter:
        camofox_ids = [s for s in source_filter if s in CAMOFOX_SOURCES]
    else:
        camofox_ids = list(CAMOFOX_SOURCES.keys())

    for sid in camofox_ids:
        try:
            items = await fetch_source(sid)
            all_items.extend(items)
            logger.info(f"[unified] camofox:{sid}: {len(items)} items")
        except Exception as e:
            logger.error(f"[unified] camofox:{sid}: failed: {e}")

    # Phase 2: NewsNow sources (Chinese)
    if source_filter:
        newsnow_ids = [s for s in source_filter if s in NEWSNOW_SOURCES]
    else:
        newsnow_ids = list(NEWSNOW_SOURCES.keys())

    for sid in newsnow_ids:
        try:
            items = fetch_newsnow_source(sid)
            all_items.extend(items)
            logger.info(f"[unified] newsnow:{sid}: {len(items)} items")
        except Exception as e:
            logger.error(f"[unified] newsnow:{sid}: failed: {e}")

    logger.info(f"[unified] total: {len(all_items)} items from {len(camofox_ids) + len(newsnow_ids)} sources")
    return all_items


async def daily_push(source_filter: Optional[list[str]] = None) -> dict:
    """Full Muse daily routine.

    Returns stats dict with results.
    """
    start = time.time()

    # Step 1: Crawl all sources
    items = await fetch_all_unified(source_filter)

    # Step 2: Embed and rank (via interest vector)
    # (Placeholder — bge-small integration comes in the next PR)
    ranked = items

    # Step 3: Pick top 50
    top50 = ranked[:50]

    elapsed = time.time() - start
    logger.info(f"[muse] daily push: {len(items)} total → {len(top50)} top, {elapsed:.1f}s")

    return {
        "total_items": len(items),
        "top_items": len(top50),
        "sources": list(set(i.source for i in items if i.source)),
        "elapsed_seconds": round(elapsed, 1),
        "items": top50,
    }
