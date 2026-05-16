"""NewsNow connector — Chinese hot lists via newsnow.busiyi.world API.

This is the "easy path": we just call NewsNow's hosted API.
No crawling, no browser — just HTTP requests.

NewsNow covers 44 Chinese sources including:
  weibo, baidu, zhihu, bilibili, douyin, toutiao, thepaper,
  wallstreetcn, 36kr, sspai, v2ex, juejin, ithome, ...

We pick the most relevant subset for Muse (tech + finance + general).
"""

from __future__ import annotations

import json
import logging
import time
from typing import Optional

import requests

from muse.types import NewsItem, SourceDef

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

NEWSNOW_API = "https://newsnow.busiyi.world/api/s"
# The busiyi.world API returns items keyed by source ID — same IDs as NewsNow
TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

# Which NewsNow sources to pull for Muse
# Picked for relevance: tech + finance + general interest
NEWSNOW_SOURCES: dict[str, SourceDef] = {
    "weibo": SourceDef(
        id="weibo", name="微博热搜", interval=180, category="china",
        home="https://weibo.com", max_items=30,
    ),
    "baidu": SourceDef(
        id="baidu", name="百度热搜", interval=300, category="china",
        home="https://top.baidu.com", max_items=30,
    ),
    "zhihu": SourceDef(
        id="zhihu", name="知乎热榜", interval=600, category="china",
        home="https://www.zhihu.com", max_items=30,
    ),
    "bilibili": SourceDef(
        id="bilibili", name="B站热门", interval=600, category="china",
        home="https://www.bilibili.com", max_items=30,
    ),
    "36kr": SourceDef(
        id="36kr", name="36氪", interval=600, category="china",
        home="https://36kr.com", max_items=30,
    ),
    "sspai": SourceDef(
        id="sspai", name="少数派", interval=1800, category="china",
        home="https://sspai.com", max_items=20,
    ),
    "v2ex": SourceDef(
        id="v2ex", name="V2EX", interval=600, category="china",
        home="https://v2ex.com", max_items=20,
    ),
    "wallstreetcn": SourceDef(
        id="wallstreetcn", name="华尔街见闻", interval=300, category="china",
        home="https://wallstreetcn.com", max_items=20,
    ),
    "juejin": SourceDef(
        id="juejin", name="掘金", interval=1800, category="china",
        home="https://juejin.cn", max_items=20,
    ),
}


def list_newsnow_sources() -> list[SourceDef]:
    return list(NEWSNOW_SOURCES.values())


# ---------------------------------------------------------------------------
# Fetch a single NewsNow source
# ---------------------------------------------------------------------------

def fetch_newsnow_source(source_id: str) -> list[NewsItem]:
    """Fetch hot items from NewsNow API for one source.

    Uses PySocks SOCKS5 proxy to bypass Cloudflare.
    Returns list of NewsItem. Empty list on failure.
    """
    source = NEWSNOW_SOURCES.get(source_id)
    if not source:
        raise ValueError(f"Unknown NewsNow source: {source_id}")

    try:
        data = _socks_get(f"{NEWSNOW_API}?id={source_id}")
        if data.get("status") not in ("success", "cache"):
            logger.warning(f"[newsnow] {source_id}: bad status {data.get('status')}")
            return []

        raw_items = data.get("items", [])
        items: list[NewsItem] = []
        for item in raw_items[:source.max_items]:
            title = item.get("title", "")
            if not title or not isinstance(title, str):
                continue
            items.append(NewsItem(
                id=item.get("id", title),
                title=title,
                url=item.get("url", ""),
                mobile_url=item.get("mobileUrl"),
                pub_date=item.get("pubDate"),
                source=f"newsnow:{source_id}",
                extra=item.get("extra"),
            ))

        return items

    except Exception as e:
        logger.error(f"[newsnow] {source_id}: failed: {e}")
        return []


def _socks_get(url: str, timeout: int = 15) -> dict:
    """Low-level HTTPS GET via SOCKS5 proxy.

    Uses PySocks directly instead of ``requests`` to avoid ALL_PROXY
    environment variable conflicts with the hermes-agent venv setup.
    """
    from urllib.parse import urlparse
    import socks as socks_module
    import socket
    import ssl

    parsed = urlparse(url)
    host = parsed.hostname
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    # SOCKS5 connection
    sock = socks_module.socksocket()
    sock.set_proxy(socks_module.SOCKS5, "127.0.0.1", 7890)
    sock.settimeout(timeout)
    sock.connect((host, 443))

    # TLS
    ctx = ssl.create_default_context()
    ss = ctx.wrap_socket(sock, server_hostname=host)

    # HTTP/1.1 GET
    ss.sendall(
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: {USER_AGENT}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
        .encode()
    )

    # Read response
    data = b""
    while True:
        chunk = ss.read(4096)
        if not chunk:
            break
        data += chunk

    ss.close()

    # Parse body — handle both \r\n and \n line endings
    separator = b"\r\n\r\n"
    if separator in data:
        body = data.split(separator, 1)[1]
    else:
        body = data.split(b"\n\n", 1)[1]
    body = body.strip()
    return json.loads(body)


def fetch_all_newsnow(source_ids: Optional[list[str]] = None) -> dict[str, list[NewsItem]]:
    """Fetch multiple NewsNow sources.

    Returns {source_id: [NewsItem, ...]}.
    """
    if source_ids is None:
        source_ids = list(NEWSNOW_SOURCES.keys())

    results: dict[str, list[NewsItem]] = {}
    for sid in source_ids:
        items = fetch_newsnow_source(sid)
        if items:
            results[sid] = items
            logger.info(f"[newsnow] {sid}: {len(items)} items")
        else:
            logger.warning(f"[newsnow] {sid}: 0 items (rate limited?)")

    return results
