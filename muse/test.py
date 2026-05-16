#!/usr/bin/env python3
"""Test Muse crawlers — verify Camofox-based sources.

Usage:
    python3 -m muse.test              # Test all sources
    python3 -m muse.test hackernews   # Test one source
"""

from __future__ import annotations

import asyncio
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("muse.test")


async def test_crawler(source_id: str) -> None:
    """Test crawling a single source."""
    from muse.crawler import crawl_source

    print(f"\n{'='*60}")
    print(f"  Testing: {source_id}")
    print(f"  Press Ctrl+C to skip")
    print(f"{'='*60}")

    start = time.time()
    try:
        items = await crawl_source(source_id)
        elapsed = time.time() - start
        print(f"  ✓ {len(items)} items in {elapsed:.1f}s")
        for i, item in enumerate(items[:5], 1):
            print(f"    {i}. {item.title[:80]}")
            if item.extra:
                extra_str = " | ".join(f"{k}={v}" for k, v in item.extra.items() if v)
                if extra_str:
                    print(f"       [{extra_str}]")
        if len(items) > 5:
            print(f"    ... and {len(items) - 5} more")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ✗ FAILED after {elapsed:.1f}s: {e}")


async def test_newsnow(source_id: str) -> None:
    """Test fetching a NewsNow source."""
    from muse.newsnow import fetch_newsnow_source

    print(f"\n{'='*60}")
    print(f"  Testing NewsNow: {source_id}")
    print(f"{'='*60}")

    start = time.time()
    try:
        items = fetch_newsnow_source(source_id)
        elapsed = time.time() - start
        print(f"  ✓ {len(items)} items in {elapsed:.1f}s")
        for i, item in enumerate(items[:5], 1):
            print(f"    {i}. {item.title[:80]}")
        if len(items) > 5:
            print(f"    ... and {len(items) - 5} more")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ✗ FAILED after {elapsed:.1f}s: {e}")


async def main():
    from muse.sources import list_sources
    from muse.newsnow import list_newsnow_sources
    from muse.camofox import check_available

    # Check Camofox
    camofox_ok = check_available()
    print(f"\nCamofox browser: {'✓ ONLINE' if camofox_ok else '✗ OFFLINE'}")
    if not camofox_ok:
        print("  Start with: cd /Volumes/Lab/camofox-browser && npm start")
        print("  (Or it should be running via launchctl)")

    # Check NewsNow API
    print(f"NewsNow API: https://newsnow.busiyi.world/api/s")

    if len(sys.argv) > 1:
        # Test specific source
        arg = sys.argv[1]

        # Check if it's a Camofox source
        sources = list_sources()
        source_ids = [s.id for s in sources]
        if arg in source_ids:
            await test_crawler(arg)
            return

        # Check if it's a NewsNow source
        newsnow_ids = [s.id for s in list_newsnow_sources()]
        if arg in newsnow_ids:
            await test_newsnow(arg)
            return

        print(f"Unknown source: {arg}")
        print(f"Camofox sources: {', '.join(source_ids)}")
        print(f"NewsNow sources: {', '.join(newsnow_ids)}")
        return

    # Test all Camofox sources
    print(f"\n{'='*60}")
    print(f"  Testing ALL Camofox sources ({len(list_sources())} total)")
    print(f"{'='*60}")

    for source in list_sources():
        await test_crawler(source.id)
        # Small delay between sources to be polite to Camofox
        await asyncio.sleep(1)

    # Test a few NewsNow sources
    print(f"\n{'='*60}")
    print(f"  Testing NewsNow sources (sample)")
    print(f"{'='*60}")

    for sid in ["weibo", "zhihu", "36kr"]:
        await test_newsnow(sid)
        await asyncio.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"  DONE")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
