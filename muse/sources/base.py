"""Abstract base class for content sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from muse.models import NewsItem


class SourceClient(ABC):
    """Base class for all content sources."""

    source_type: str = "abstract"

    @abstractmethod
    async def fetch(self) -> list[NewsItem]:
        """Fetch content items from this source."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if source is reachable."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(type={self.source_type})>"
