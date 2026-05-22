"""Content fetcher — extracts article text from URLs."""

from __future__ import annotations

import re
from typing import Optional

import httpx


# Blocks that usually contain navigation / ads / scripts
_NOISE_TAGS = re.compile(
    r"<(script|style|nav|header|footer|aside|form|iframe|noscript)[^>]*>.*?</\1>",
    re.DOTALL | re.IGNORECASE,
)

# Tags whose text we want to keep
_CONTENT_TAGS = re.compile(
    r"<(p|div|article|section|h[1-6]|li|td|blockquote|pre)[^>]*>",
    re.IGNORECASE,
)

# Inline tags we want to keep as spaces
_INLINE_TAGS = re.compile(r"<(br|hr)\s*/?>", re.IGNORECASE)

# Any remaining HTML tags
_ALL_TAGS = re.compile(r"<[^>]+>")

# Collapse whitespace
_WHITESPACE = re.compile(r"\s+")


def _extract_text(html: str) -> str:
    """Crude but effective HTML-to-text extraction without external deps."""
    # Remove noise blocks
    text = _NOISE_TAGS.sub(" ", html)
    # Replace inline breaks with newlines
    text = _INLINE_TAGS.sub("\n", text)
    # Remove all remaining tags
    text = _ALL_TAGS.sub(" ", text)
    # Decode common entities
    text = (
        text.replace("&nbsp;", " ")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    # Collapse whitespace
    text = _WHITESPACE.sub(" ", text).strip()
    # Paragraph breaks: detect sentence endings + capital letters
    text = re.sub(r"([.!?])\s+([A-Z])", r"\1\n\n\2", text)
    return text


def _extract_title(html: str) -> Optional[str]:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if m:
        return _WHITESPACE.sub(" ", m.group(1)).strip()
    return None


async def fetch_article(url: str, timeout: float = 15.0) -> dict:
    """Fetch URL and extract article text.

    Returns {"title": str, "text": str, "url": str, "ok": bool, "error": str|None}
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True) as client:
            r = await client.get(url)
            r.raise_for_status()
            html = r.text
            title = _extract_title(html)
            text = _extract_text(html)
            # Truncate if excessively long (likely extracted nav/footer residue)
            if len(text) > 50_000:
                text = text[:50_000] + "\n\n[Content truncated]"
            return {
                "title": title or "",
                "text": text,
                "url": str(r.url),
                "ok": True,
                "error": None,
            }
    except Exception as exc:
        return {
            "title": "",
            "text": "",
            "url": url,
            "ok": False,
            "error": str(exc),
        }
