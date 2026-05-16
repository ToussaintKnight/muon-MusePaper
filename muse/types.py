"""Muse data types — matching NewsNow's NewsItem interface."""

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class NewsItem:
    """A single item from any source (NewsNow or Camofox-crawled).

    Mirrors NewsNow's ``{ id, title, url, mobileUrl?, pubDate?, extra? }``.
    """
    id: str | int                # unique identifier
    title: str                   # display title
    url: str                     # canonical URL
    mobile_url: Optional[str] = None
    pub_date: Optional[int | str] = None  # epoch ms or ISO string
    extra: Optional[dict[str, Any]] = None

    # Muse-specific metadata
    source: str = ""             # source id, e.g. "hackernews"
    score: float = 0.0           # relevance score after cosine ranking
    embed_256: Optional[list[float]] = None  # cached embedding

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class SourceDef:
    """Definition of a data source — NewsNow-style metadata."""
    id: str                      # unique source id, e.g. "hackernews"
    name: str                    # display name
    interval: int                # refresh interval in seconds
    category: str = "global"     # "global" | "china" (for NewsNow) | custom
    enabled: bool = True
    max_items: int = 30
    # For Camofox: the URL to open
    url: str = ""
    # How the snapshot should be structured (guide for parser)
    parser_hint: str = "default"  # "hackernews" | "github-trending" | "producthunt" | ...
    home: str = ""               # homepage URL
