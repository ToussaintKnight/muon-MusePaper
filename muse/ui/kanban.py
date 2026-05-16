"""Kanban session state management."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from muse.models import NewsItem, UserProfile, SaveResult


@dataclass
class KanbanSession:
    """One user interaction session."""

    session_id: str
    items: list[NewsItem]
    columns: dict[str, list[str]] = field(default_factory=dict)
    profile_snapshot: Optional[UserProfile] = None

    @classmethod
    def create(cls, items: list[NewsItem], profile: UserProfile) -> KanbanSession:
        return cls(
            session_id=str(uuid.uuid4())[:8],
            items=items,
            columns={"inbox": [item.id for item in items]},
            profile_snapshot=profile,
        )

    def move_item(self, item_id: str, to_bucket: str) -> None:
        """Move an item to a bucket (removing from all other buckets)."""
        for bucket, ids in self.columns.items():
            if item_id in ids and bucket != to_bucket:
                ids.remove(item_id)
        self.columns.setdefault(to_bucket, []).append(item_id)

    def get_bucket_items(self, bucket: str) -> list[NewsItem]:
        """Return NewsItem objects in a bucket."""
        ids = set(self.columns.get(bucket, []))
        return [item for item in self.items if item.id in ids]

    def get_ignored_items(self) -> list[NewsItem]:
        """Return items still in inbox (never moved)."""
        moved = set()
        for bucket, ids in self.columns.items():
            if bucket != "inbox":
                moved.update(ids)
        return [item for item in self.items if item.id not in moved]

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "items": [item.to_dict() for item in self.items],
            "columns": self.columns,
        }
