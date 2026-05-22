"""Core domain models for Muse."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np


# ── NewsItem ───────────────────────────────────────────────────────────

@dataclass
class NewsItem:
    """Universal content item from any source."""

    id: str
    title: str
    url: str
    source: str           # e.g. "newsnow_weibo", "rsshub_hn"
    source_type: str      # "newsnow" | "rsshub" | "native" | "camofox"
    pub_date: Optional[datetime] = None
    heat_score: Optional[int] = None
    extra: dict = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    score: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "source_type": self.source_type,
            "pub_date": self.pub_date.isoformat() if self.pub_date else None,
            "heat_score": self.heat_score,
            "extra": self.extra,
            "score": self.score,
        }


# ── EngagementEvent ────────────────────────────────────────────────────

@dataclass
class EngagementEvent:
    """One user action on one item."""

    item_id: str
    item_title: str
    bucket: str           # "tools" | "interested" | "not_interested" | "ignored"
    item_embedding: list[float]
    timestamp: datetime
    top_tag: str
    source: str = ""

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "item_title": self.item_title,
            "bucket": self.bucket,
            "item_embedding": self.item_embedding,
            "timestamp": self.timestamp.isoformat(),
            "top_tag": self.top_tag,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, d: dict) -> EngagementEvent:
        return cls(
            item_id=d["item_id"],
            item_title=d["item_title"],
            bucket=d["bucket"],
            item_embedding=d["item_embedding"],
            timestamp=datetime.fromisoformat(d["timestamp"]),
            top_tag=d["top_tag"],
            source=d.get("source", ""),
        )


# ── UserProfile ────────────────────────────────────────────────────────

@dataclass
class ReadingItem:
    """One article in the user's reading queue."""

    id: str
    title: str
    url: str
    source: str
    status: str = "unread"          # "unread" | "read" | "archived"
    added_at: datetime = field(default_factory=datetime.now)
    read_at: Optional[datetime] = None
    summary: Optional[str] = None   # LLM-generated distillation
    content: Optional[str] = None   # extracted article text
    score: Optional[float] = None   # relevance score at time of queueing

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "status": self.status,
            "added_at": self.added_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "summary": self.summary,
            "content": self.content,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ReadingItem:
        return cls(
            id=d["id"],
            title=d["title"],
            url=d["url"],
            source=d["source"],
            status=d.get("status", "unread"),
            added_at=datetime.fromisoformat(d["added_at"]),
            read_at=datetime.fromisoformat(d["read_at"]) if d.get("read_at") else None,
            summary=d.get("summary"),
            content=d.get("content"),
            score=d.get("score"),
        )


@dataclass
class UserProfile:
    """Single-user interest profile."""

    version: int = 3
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    interest_vector: list[float] = field(default_factory=lambda: [0.0] * 256)
    keyword_weights: dict[str, float] = field(default_factory=dict)
    history: list[EngagementEvent] = field(default_factory=list)
    daily_metrics_history: list[dict] = field(default_factory=list)
    reading_queue: list[ReadingItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    save_count: int = 0

    # Transient: not persisted
    _vector_np: Optional[np.ndarray] = field(default=None, repr=False)

    def vector(self) -> np.ndarray:
        """Return interest vector as numpy array (cached)."""
        if self._vector_np is None:
            self._vector_np = np.array(self.interest_vector, dtype=np.float32)
        return self._vector_np

    def set_vector(self, vec: np.ndarray) -> None:
        """Set interest vector from numpy array."""
        self.interest_vector = vec.tolist()
        self._vector_np = vec

    def save(self, path: Path | str) -> None:
        """Serialize to JSON."""
        path = Path(path)
        data = {
            "version": self.version,
            "embedding_model": self.embedding_model,
            "interest_vector": self.interest_vector,
            "keyword_weights": self.keyword_weights,
            "history": [e.to_dict() for e in self.history[-500:]],  # keep last 500
            "daily_metrics_history": self.daily_metrics_history[-90:],  # last 90 days
            "reading_queue": [r.to_dict() for r in self.reading_queue[-200:]],  # keep last 200
            "created_at": self.created_at.isoformat(),
            "updated_at": datetime.now().isoformat(),
            "save_count": self.save_count,
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: Path | str) -> UserProfile:
        """Deserialize from JSON."""
        path = Path(path)
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = cls(
            version=data.get("version", 3),
            embedding_model=data.get("embedding_model", "BAAI/bge-small-zh-v1.5"),
            interest_vector=data.get("interest_vector", [0.0] * 256),
            keyword_weights=data.get("keyword_weights", {}),
            history=[EngagementEvent.from_dict(e) for e in data.get("history", [])],
            daily_metrics_history=data.get("daily_metrics_history", []),
            reading_queue=[ReadingItem.from_dict(r) for r in data.get("reading_queue", [])],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat())),
            save_count=data.get("save_count", 0),
        )
        return profile

    def add_event(self, event: EngagementEvent) -> None:
        """Append engagement event."""
        self.history.append(event)
        self.save_count += 1
        self.updated_at = datetime.now()

    def get_weekly_events(self) -> list[EngagementEvent]:
        """Return events from the last 7 days."""
        cutoff = datetime.now() - __import__("datetime").timedelta(days=7)
        return [e for e in self.history if e.timestamp > cutoff]

    def get_today_events(self) -> list[EngagementEvent]:
        """Return events from today."""
        today = datetime.now().date()
        return [e for e in self.history if e.timestamp.date() == today]


# ── TagNode ────────────────────────────────────────────────────────────

@dataclass
class TagNode:
    """Node in the interest tag tree."""

    id: str
    name: str
    path: str
    keywords: list[str] = field(default_factory=list)
    children: list[TagNode] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "keywords": self.keywords,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, d: dict) -> TagNode:
        return cls(
            id=d["id"],
            name=d["name"],
            path=d.get("path", d["name"]),
            keywords=d.get("keywords", []),
            children=[TagNode.from_dict(c) for c in d.get("children", [])],
        )

    def flatten(self) -> list[TagNode]:
        """Return self + all descendants."""
        result = [self]
        for child in self.children:
            result.extend(child.flatten())
        return result


# ── KanbanSession / SaveResult ─────────────────────────────────────────

@dataclass
class SaveResult:
    """Result of a save operation."""

    vector_delta: float
    notion_synced: int
    new_top_tags: list[str]
    effectiveness_score: Optional[float] = None


@dataclass
class KanbanSession:
    """One user interaction session."""

    session_id: str
    items: list[NewsItem]
    columns: dict[str, list[str]] = field(default_factory=dict)  # bucket -> item_ids
    profile_snapshot: Optional[UserProfile] = None

    def move_item(self, item_id: str, from_bucket: str, to_bucket: str) -> None:
        """Move an item between columns."""
        if from_bucket in self.columns and item_id in self.columns[from_bucket]:
            self.columns[from_bucket].remove(item_id)
        self.columns.setdefault(to_bucket, []).append(item_id)

    def get_bucket_items(self, bucket: str) -> list[NewsItem]:
        """Return NewsItem objects in a bucket."""
        ids = set(self.columns.get(bucket, []))
        return [item for item in self.items if item.id in ids]


# ── Utility ────────────────────────────────────────────────────────────

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """L2-normalize a vector."""
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm
