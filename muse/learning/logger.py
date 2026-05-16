"""Feedback logger — persists engagement events."""

from __future__ import annotations

from datetime import datetime

from muse.models import EngagementEvent, UserProfile


class FeedbackLogger:
    """Log engagement events to profile history."""

    def log_event(
        self,
        profile: UserProfile,
        item_id: str,
        item_title: str,
        bucket: str,
        item_embedding: list[float],
        top_tag: str,
        source: str = "",
    ) -> EngagementEvent:
        """Create and store an engagement event."""
        event = EngagementEvent(
            item_id=item_id,
            item_title=item_title,
            bucket=bucket,
            item_embedding=item_embedding,
            timestamp=datetime.now(),
            top_tag=top_tag,
            source=source,
        )
        profile.add_event(event)
        return event
