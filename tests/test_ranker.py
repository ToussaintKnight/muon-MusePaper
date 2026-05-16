"""Tests for RankerEngine."""

import numpy as np
import pytest

from muse.models import NewsItem, UserProfile
from muse.ranker import RankerEngine


class TestRankerEngine:
    def _make_item(self, title: str, embedding: list[float]) -> NewsItem:
        return NewsItem(
            id="1",
            title=title,
            url="http://test.com",
            source="test",
            source_type="native",
            embedding=np.array(embedding, dtype=np.float32),
        )

    def _make_profile(self, vector: list[float]) -> UserProfile:
        return UserProfile(interest_vector=vector)

    def test_score_identical_vector(self):
        vec = [1.0, 0.0, 0.0]
        item = self._make_item("Test", vec)
        profile = self._make_profile(vec)
        
        ranker = RankerEngine()
        score = ranker._score_item(item, profile)
        assert score == pytest.approx(1.0, rel=1e-4)

    def test_score_orthogonal_vector(self):
        vec = [1.0, 0.0, 0.0]
        item = self._make_item("Test", [0.0, 1.0, 0.0])
        profile = self._make_profile(vec)
        
        ranker = RankerEngine()
        score = ranker._score_item(item, profile)
        assert score == pytest.approx(0.0, abs=1e-4)

    def test_diversity_filter(self):
        items = [
            NewsItem(id=f"i{n}", title=f"Item {n}", url="http://t.com",
                     source="source_a", source_type="native",
                     embedding=np.array([1.0, 0.0, 0.0], dtype=np.float32))
            for n in range(5)
        ]
        for i in items:
            i.score = 1.0
        
        ranker = RankerEngine(diversity_max_per_source=2)
        diverse = ranker._apply_diversity(items)
        assert len(diverse) == 2  # capped at 2 per source

    def test_rank_and_sort(self):
        items = [
            self._make_item("High", [1.0, 0.0, 0.0]),
            self._make_item("Low", [-1.0, 0.0, 0.0]),
            self._make_item("Mid", [0.5, 0.0, 0.0]),
        ]
        profile = self._make_profile([1.0, 0.0, 0.0])
        
        ranker = RankerEngine()
        ranked = ranker.score_and_rank(items, profile, top_n=10)
        
        assert len(ranked) == 3
        assert ranked[0].title == "High"
        assert ranked[1].title == "Mid"
        assert ranked[2].title == "Low"
