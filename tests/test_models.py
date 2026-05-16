"""Tests for core models."""

import json
import tempfile
from datetime import datetime

import numpy as np
import pytest

from muse.models import (
    EngagementEvent,
    NewsItem,
    TagNode,
    UserProfile,
    cosine_similarity,
    normalize_vector,
)


class TestCosineSimilarity:
    def test_identical_vectors(self):
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = np.array([1.0, 0.0])
        b = np.array([-1.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector(self):
        a = np.array([0.0, 0.0])
        b = np.array([1.0, 0.0])
        assert cosine_similarity(a, b) == 0.0


class TestNormalizeVector:
    def test_unit_length(self):
        v = np.array([3.0, 4.0])
        n = normalize_vector(v)
        assert np.linalg.norm(n) == pytest.approx(1.0)

    def test_zero_vector_unchanged(self):
        v = np.array([0.0, 0.0])
        n = normalize_vector(v)
        assert np.all(n == 0.0)


class TestUserProfile:
    def test_default_vector(self):
        p = UserProfile()
        assert len(p.interest_vector) == 256
        assert all(v == 0.0 for v in p.interest_vector)

    def test_vector_numpy_conversion(self):
        p = UserProfile(interest_vector=[0.1] * 256)
        vec = p.vector()
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (256,)

    def test_set_vector(self):
        p = UserProfile()
        new_vec = np.array([0.5] * 256)
        p.set_vector(new_vec)
        assert p.interest_vector == [0.5] * 256

    def test_save_and_load(self):
        p = UserProfile(
            interest_vector=[0.1] * 256,
            keyword_weights={"AI/ML": 1.5},
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        
        p.save(path)
        loaded = UserProfile.load(path)
        
        assert loaded.interest_vector == p.interest_vector
        assert loaded.keyword_weights == p.keyword_weights
        assert loaded.version == p.version

    def test_add_event(self):
        p = UserProfile()
        event = EngagementEvent(
            item_id="123",
            item_title="Test",
            bucket="tools",
            item_embedding=[0.0] * 256,
            timestamp=datetime.now(),
            top_tag="AI/ML",
        )
        p.add_event(event)
        assert len(p.history) == 1
        assert p.save_count == 1

    def test_load_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = tmpdir + "/nonexistent.json"
            p = UserProfile.load(path)
            assert isinstance(p, UserProfile)


class TestTagNode:
    def test_flatten(self):
        root = TagNode(
            id="root", name="Root", path="Root",
            children=[
                TagNode(id="c1", name="C1", path="Root → C1"),
                TagNode(id="c2", name="C2", path="Root → C2"),
            ]
        )
        flat = root.flatten()
        assert len(flat) == 3
        assert {n.id for n in flat} == {"root", "c1", "c2"}

    def test_to_from_dict(self):
        node = TagNode(
            id="test", name="Test", path="Test",
            keywords=["a", "b"],
            children=[TagNode(id="c1", name="C1", path="Test → C1")],
        )
        d = node.to_dict()
        restored = TagNode.from_dict(d)
        assert restored.id == node.id
        assert restored.keywords == node.keywords
        assert len(restored.children) == 1


class TestNewsItem:
    def test_to_dict(self):
        item = NewsItem(
            id="1", title="Test", url="http://test.com",
            source="test", source_type="native",
        )
        d = item.to_dict()
        assert d["title"] == "Test"
        assert d["id"] == "1"
