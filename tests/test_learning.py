"""Tests for learning layer."""

from datetime import datetime

import numpy as np
import pytest

from muse.learning.fast_loop import FastLoopUpdater, BUCKET_ETA
from muse.learning.slow_loop import SlowLoopOptimizer, _bucket_target
from muse.models import EngagementEvent, UserProfile


class TestFastLoopUpdater:
    def test_update_vector_tools(self):
        profile = UserProfile()
        vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        profile.set_vector(vec)
        
        # Item at 90 degrees — non-collinear so normalization doesn't undo
        item_emb = [0.0, 1.0, 0.0]
        events = [
            EngagementEvent(
                item_id="1", item_title="Test", bucket="tools",
                item_embedding=item_emb, timestamp=datetime.now(), top_tag="test",
            )
        ]
        
        updater = FastLoopUpdater()
        new_vec, delta = updater.update_vector(profile, events)
        
        # Vector should rotate toward item (y-component should increase)
        assert new_vec[1] > 0.0  # pulled toward y-axis
        assert delta > 0  # vector changed
        assert np.linalg.norm(new_vec) == pytest.approx(1.0)  # normalized

    def test_update_vector_not_interested(self):
        profile = UserProfile()
        vec = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        profile.set_vector(vec)
        
        item_emb = [1.0, 0.0, 0.0]
        events = [
            EngagementEvent(
                item_id="1", item_title="Test", bucket="not_interested",
                item_embedding=item_emb, timestamp=datetime.now(), top_tag="test",
            )
        ]
        
        updater = FastLoopUpdater()
        new_vec, delta = updater.update_vector(profile, events)
        
        # Negative eta should push away
        # But since item is same direction, pushing away means... 
        # Actually EMA with negative eta: v += -0.03 * (item - v)
        # If v = item, then v += -0.03 * 0 = no change
        # Let's use different vectors
        item_emb = [0.0, 1.0, 0.0]
        events[0].item_embedding = item_emb
        new_vec, delta = updater.update_vector(profile, events)
        assert delta > 0

    def test_bucket_eta_values(self):
        assert BUCKET_ETA["tools"] > BUCKET_ETA["interested"] > 0
        assert BUCKET_ETA["not_interested"] < 0
        assert BUCKET_ETA["ignored"] == 0


class TestSlowLoopOptimizer:
    def test_should_trigger(self):
        profile = UserProfile()
        opt = SlowLoopOptimizer(min_events=5)
        
        # Not enough events
        assert not opt.should_trigger(profile)
        
        # Add 5 events
        for i in range(5):
            profile.add_event(EngagementEvent(
                item_id=str(i), item_title="T", bucket="tools",
                item_embedding=[0.0] * 256, timestamp=datetime.now(), top_tag="t",
            ))
        assert opt.should_trigger(profile)

    def test_optimize_keyword_weights(self):
        profile = UserProfile()
        # Add enough mixed signals for same tag (need >= 10 events)
        for _ in range(8):
            profile.add_event(EngagementEvent(
                item_id="1", item_title="T", bucket="tools",
                item_embedding=[0.0] * 256, timestamp=datetime.now(), top_tag="AI/ML",
            ))
        for _ in range(3):
            profile.add_event(EngagementEvent(
                item_id="2", item_title="T", bucket="not_interested",
                item_embedding=[0.0] * 256, timestamp=datetime.now(), top_tag="AI/ML",
            ))
        
        opt = SlowLoopOptimizer()
        weights = opt.optimize_keyword_weights(profile)
        
        # Positive signals dominate → weight should increase
        assert "AI/ML" in weights
        assert weights["AI/ML"] > 1.0


class TestBucketTarget:
    def test_targets(self):
        assert _bucket_target("tools") == 1.0
        assert _bucket_target("interested") == 0.5
        assert _bucket_target("not_interested") == -0.5
        assert _bucket_target("ignored") == -0.1
