"""MuseEngine — main orchestrator."""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Optional

import numpy as np

from muse.decoder import VectorDecoder
from muse.effectiveness import compute_daily_metrics
from muse.embedder import encode
from muse.learning.fast_loop import FastLoopUpdater
from muse.learning.logger import FeedbackLogger
from muse.learning.slow_loop import SlowLoopOptimizer
from muse.models import (
    EngagementEvent,
    NewsItem,
    ReadingItem,
    SaveResult,
    UserProfile,
    cosine_similarity,
)
from muse.ranker import RankerEngine
from muse.sources.aggregator import SourceAggregator
from muse.sources.native import NativeAPIClient
from muse.sources.newsnow import NewsNowClient
from muse.sources.rsshub import RSSHubClient
from muse.ui.kanban import KanbanSession
from muse.ui.notion_sync import NotionSync

PROFILE_PATH = Path(__file__).parent.parent / "data" / "profile.json"


class MuseEngine:
    """Main entry point. Owns the full pipeline."""

    def __init__(
        self,
        profile_path: Optional[Path] = None,
        enable_notion: bool = True,
        enable_rsshub: bool = True,
    ):
        self.profile_path = profile_path or PROFILE_PATH
        self.profile = UserProfile.load(self.profile_path)
        self.enable_notion = enable_notion
        self.enable_rsshub = enable_rsshub

        # Subsystems
        self.ranker = RankerEngine()
        self.decoder = VectorDecoder()
        self.fast_loop = FastLoopUpdater()
        self.slow_loop = SlowLoopOptimizer()
        self.logger = FeedbackLogger()
        self.notion = NotionSync() if enable_notion else None

        # Sources (built lazily)
        self._aggregator: Optional[SourceAggregator] = None

    def _get_aggregator(self) -> SourceAggregator:
        """Build source aggregator with available clients."""
        if self._aggregator is None:
            clients: list = [NewsNowClient(), NativeAPIClient()]
            if self.enable_rsshub:
                clients.append(RSSHubClient())
            self._aggregator = SourceAggregator(clients)
        return self._aggregator

    async def run_morning_routine(self, top_n: int = 50) -> list[NewsItem]:
        """
        Full pipeline: fetch → embed → rank → return top N items.
        """
        aggregator = self._get_aggregator()
        
        # Fetch from all sources
        items = await aggregator.fetch_all()
        
        if not items:
            return []
        
        # Rank against interest vector
        ranked = self.ranker.score_and_rank(items, self.profile, top_n=top_n)
        return ranked

    async def run_newspaper_issue(self, top_n: int = 100) -> tuple["NewspaperDraftIssue", KanbanSession]:
        """
        Full newspaper production pipeline: fetch → rank → layout → abstracts → draft.
        Returns (draft_issue, kanban_session).
        """
        from muse.agents.layout_agent import LayoutAgent, NewspaperDraftIssue
        from muse.agents.abstract_agent import AbstractAgent

        # 1. Fetch and rank
        items = await self.run_morning_routine(top_n=top_n)

        # 2. Layout
        layout_agent = LayoutAgent(self.decoder)
        slots = layout_agent.categorize_items(items)
        pages = layout_agent.build_pages(slots)

        # 3. Abstract preparation
        abstract_agent = AbstractAgent()
        pages = await abstract_agent.prepare_abstracts(pages)

        # 4. Create linked Kanban session (all items start in inbox = ignored)
        session = KanbanSession.create(items, self.profile)

        issue = NewspaperDraftIssue(
            issue_date=__import__("datetime").datetime.now().strftime("%Y-%m-%d"),
            issue_number=self.profile.save_count + 1,
            pages=pages,
            session_id=session.session_id,
        )
        return issue, session

    async def handle_save(self, session: KanbanSession) -> SaveResult:
        """
        Process a Kanban save:
          1. Log engagement events
          2. Fast-loop vector update
          3. Notion sync (Tools)
          4. Slow-loop trigger check
          5. Compute daily effectiveness
          6. Persist profile
        """
        events: list[EngagementEvent] = []
        
        # Build events from each bucket
        for bucket in ["tools", "interested", "not_interested"]:
            bucket_items = session.get_bucket_items(bucket)
            for item in bucket_items:
                # Determine top matching tag for this item
                top_tag = self._guess_top_tag(item)
                
                event = self.logger.log_event(
                    profile=self.profile,
                    item_id=item.id,
                    item_title=item.title,
                    bucket=bucket,
                    item_embedding=item.embedding.tolist() if item.embedding is not None else [0.0] * 256,
                    top_tag=top_tag,
                    source=item.source,
                )
                events.append(event)
        
        # Ignored items
        ignored_items = session.get_ignored_items()
        for item in ignored_items:
            event = self.logger.log_event(
                profile=self.profile,
                item_id=item.id,
                item_title=item.title,
                bucket="ignored",
                item_embedding=item.embedding.tolist() if item.embedding is not None else [0.0] * 256,
                top_tag=self._guess_top_tag(item),
                source=item.source,
            )
            events.append(event)
        
        # Fast loop: update vector
        new_vector, vector_delta = self.fast_loop.update_vector(self.profile, events)
        
        # Fast loop: update keyword weights
        self.fast_loop.update_topic_weights(self.profile, events)
        
        # Sync Tools to Notion
        tools = session.get_bucket_items("tools")
        notion_synced = 0
        if self.notion and self.notion.is_configured():
            notion_synced = await self.notion.batch_sync(tools)
        
        # Populate reading queue with Interested items
        interested = session.get_bucket_items("interested")
        for item in interested:
            # Skip duplicates by URL
            if not any(r.url == item.url for r in self.profile.reading_queue):
                self.profile.reading_queue.append(ReadingItem(
                    id=item.id,
                    title=item.title,
                    url=item.url,
                    source=item.source,
                    score=item.score,
                ))
        
        # Slow loop: trigger if enough data
        if self.slow_loop.should_trigger(self.profile):
            self.slow_loop.optimize_keyword_weights(self.profile)
        
        # Daily effectiveness metrics
        today_events = self.profile.get_today_events()
        yesterday_vec = self._get_yesterday_vector()
        today_top = self.decoder.get_top_tags(new_vector, k=5)
        yesterday_top = self._get_yesterday_top_tags()
        
        # Count Notion tools this week (approximate from events)
        weekly_tools = len([
            e for e in self.profile.get_weekly_events()
            if e.bucket == "tools"
        ])
        
        metrics = compute_daily_metrics(
            today_events=[e.to_dict() for e in today_events],
            yesterday_vector=yesterday_vec,
            today_vector=new_vector.tolist(),
            yesterday_top_tags=[t for _, t in yesterday_top],
            today_top_tags=[t for _, t in today_top],
            notion_tools_this_week=weekly_tools,
        )
        self.profile.daily_metrics_history.append(metrics.__dict__)
        
        # Persist
        self.profile.save(self.profile_path)
        
        return SaveResult(
            vector_delta=vector_delta,
            notion_synced=notion_synced,
            new_top_tags=[t for _, t in today_top],
            effectiveness_score=metrics.daily_effectiveness_score,
        )

    def get_search_queries(self) -> list[str]:
        """Decode current vector into search queries."""
        queries = self.decoder.vector_to_queries(self.profile.vector())
        return [q["query"] for q in queries]

    def get_top_tags(self, k: int = 5) -> list[tuple[float, str]]:
        """Return top-k matching tags. Empty if vector is uninitialized."""
        vec = self.profile.vector()
        # Check if vector is essentially zero (uninitialized)
        if np.linalg.norm(vec) < 0.01:
            return []
        return self.decoder.get_top_tags(vec, k=k)

    def _guess_top_tag(self, item: NewsItem) -> str:
        """Heuristic: guess the best matching tag for an item."""
        if item.embedding is None:
            return "general"
        top_tags = self.decoder.get_top_tags(item.embedding, k=1)
        return top_tags[0][1] if top_tags else "general"

    def _get_yesterday_vector(self) -> Optional[list[float]]:
        """Retrieve yesterday's vector from metrics history."""
        if not self.profile.daily_metrics_history:
            return None
        # Simplified: return current vector as proxy
        # In production, we'd store daily vector snapshots
        return None

    def _get_yesterday_top_tags(self) -> list[tuple[float, str]]:
        """Retrieve yesterday's top tags."""
        if not self.profile.daily_metrics_history:
            return []
        return []

    async def health_check(self) -> dict:
        """Check all source health."""
        aggregator = self._get_aggregator()
        source_health = await aggregator.health_check()
        return {
            "profile_exists": self.profile_path.exists(),
            "save_count": self.profile.save_count,
            "sources": source_health,
            "notion_configured": self.notion.is_configured() if self.notion else False,
        }

    async def close(self) -> None:
        """Clean up resources."""
        if self._aggregator:
            await self._aggregator.close_all()
        if self.notion:
            await self.notion.close()
