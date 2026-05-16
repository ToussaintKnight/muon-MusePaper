"""Tests for FastAPI endpoints."""

import numpy as np
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app, MuseEngine


def _fake_encode(text: str):
    """Deterministic fake embedding for tests."""
    return np.array([0.1] * 256, dtype=np.float32)


def _fake_encode_batch(texts, batch_size=32):
    return [np.array([0.1] * 256, dtype=np.float32) for _ in texts]


@pytest.fixture
def client():
    # Prevent real HTTP calls and model loading during tests
    with patch.object(MuseEngine, "run_morning_routine", return_value=[]):
        with patch.object(MuseEngine, "health_check", return_value={
            "profile_exists": True,
            "save_count": 0,
            "sources": {"newsnow": True, "native": True, "rsshub": False},
            "notion_configured": False,
        }):
            with patch("muse.embedder.encode", side_effect=_fake_encode):
                with patch("muse.embedder.encode_batch", side_effect=_fake_encode_batch):
                    with TestClient(app) as c:
                        yield c


class TestRoot:
    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        # Root now serves dashboard HTML
        assert "text/html" in resp.headers.get("content-type", "")
        assert b"Muse" in resp.content


class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "sources" in data
        assert "profile_exists" in data


class TestProfile:
    def test_get_profile(self, client):
        resp = client.get("/api/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == 2
        assert "top_tags" in data
        assert "save_count" in data


class TestSearchQueries:
    def test_get_queries(self, client):
        resp = client.get("/api/search-queries")
        assert resp.status_code == 200
        data = resp.json()
        assert "queries" in data
        assert isinstance(data["queries"], list)


class TodayItems:
    def test_get_items(self, client):
        # This will attempt real HTTP calls to sources
        # In CI, sources may fail — accept 200 or 503
        resp = client.get("/api/items/today")
        assert resp.status_code in (200, 503)


class TestSessionFlow:
    def test_start_session(self, client):
        resp = client.post("/api/session/start")
        assert resp.status_code in (200, 503)
        if resp.status_code == 200:
            data = resp.json()
            assert "session_id" in data
            assert "items" in data
