"""Ranking engine — scores and ranks items against user interest vector."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import numpy as np

from muse.embedder import encode_batch
from muse.models import NewsItem, UserProfile, cosine_similarity


class RankerEngine:
    """Scores items using cosine similarity + diversity + freshness."""

    def __init__(
        self,
        diversity_max_per_source: int = 3,
        freshness_boost_hours: int = 2,
        freshness_boost_factor: float = 1.1,
    ):
        self.diversity_max_per_source = diversity_max_per_source
        self.freshness_boost_hours = freshness_boost_hours
        self.freshness_boost_factor = freshness_boost_factor

    def score_and_rank(
        self,
        items: list[NewsItem],
        profile: UserProfile,
        top_n: int = 50,
    ) -> list[NewsItem]:
        """Score all items, apply filters, return top N."""
        # Ensure embeddings exist
        items_with_emb = self._ensure_embeddings(items)
        
        # Score each item
        for item in items_with_emb:
            item.score = self._score_item(item, profile)
        
        # Sort by score descending
        items_with_emb.sort(key=lambda x: (x.score or 0), reverse=True)
        
        # Apply diversity filter
        diverse = self._apply_diversity(items_with_emb)
        
        # Return top N
        return diverse[:top_n]

    def _score_item(self, item: NewsItem, profile: UserProfile) -> float:
        """Compute raw score for one item."""
        if item.embedding is None:
            return 0.0
        
        # Base cosine similarity
        base_score = cosine_similarity(profile.vector(), item.embedding)
        
        # Keyword boost from slow loop
        keyword_boost = 1.0
        if profile.keyword_weights:
            title_lower = item.title.lower()
            matched_weights = [
                profile.keyword_weights.get(kw, 1.0)
                for kw in profile.keyword_weights
                if kw.lower() in title_lower
            ]
            if matched_weights:
                keyword_boost = sum(matched_weights) / len(matched_weights)
        
        # Freshness boost
        freshness = 1.0
        if item.pub_date:
            age = datetime.now() - item.pub_date
            if age < timedelta(hours=self.freshness_boost_hours):
                freshness = self.freshness_boost_factor
        
        return base_score * keyword_boost * freshness

    def _ensure_embeddings(self, items: list[NewsItem]) -> list[NewsItem]:
        """Batch-encode items that lack embeddings."""
        to_encode: list[tuple[int, NewsItem]] = []
        for idx, item in enumerate(items):
            if item.embedding is None:
                to_encode.append((idx, item))
        
        if to_encode:
            texts = [f"{item.title}. {item.url}" for _, item in to_encode]
            embeddings = encode_batch(texts)
            for (idx, item), emb in zip(to_encode, embeddings):
                items[idx].embedding = emb
        
        return items

    def _apply_diversity(self, items: list[NewsItem]) -> list[NewsItem]:
        """Cap items per source to ensure diversity."""
        source_counts: dict[str, int] = {}
        diverse: list[NewsItem] = []
        for item in items:
            source = item.source or "unknown"
            count = source_counts.get(source, 0)
            if count < self.diversity_max_per_source:
                diverse.append(item)
                source_counts[source] = count + 1
        return diverse
