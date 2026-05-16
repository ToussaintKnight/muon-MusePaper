"""Slow loop optimizer — weekly batch keyword weight optimization."""

from __future__ import annotations

import math
from typing import Optional

import numpy as np

from muse.models import EngagementEvent, UserProfile


class SlowLoopOptimizer:
    """Batch optimize keyword weights using BCE + regularization."""

    def __init__(
        self,
        min_events: int = 50,
        regularization_lambda: float = 0.01,
        change_penalty_lambda: float = 0.005,
    ):
        self.min_events = min_events
        self.reg_lambda = regularization_lambda
        self.change_lambda = change_penalty_lambda

    def should_trigger(self, profile: UserProfile) -> bool:
        """Check if enough history has accumulated for optimization."""
        weekly = profile.get_weekly_events()
        return len(weekly) >= self.min_events

    def optimize_keyword_weights(self, profile: UserProfile) -> dict[str, float]:
        """
        Optimize keyword weights from weekly engagement history.
        
        Simple gradient descent on BCE loss with L2 regularization.
        """
        events = profile.get_weekly_events()
        if len(events) < 10:
            return profile.keyword_weights
        
        # Aggregate signals per tag
        tag_scores: dict[str, list[float]] = {}
        for event in events:
            tag = event.top_tag
            # Map bucket to target value
            target = _bucket_target(event.bucket)
            tag_scores.setdefault(tag, []).append(target)
        
        # Compute optimal weight per tag
        new_weights: dict[str, float] = {}
        old_weights = profile.keyword_weights
        
        for tag, targets in tag_scores.items():
            avg_target = sum(targets) / len(targets)
            old_w = old_weights.get(tag, 1.0)
            
            # Simple heuristic: weight reflects average target
            # Positive avg_target → increase weight, negative → decrease
            proposed = 1.0 + (avg_target * 2.0)
            
            # L2 regularization toward 1.0
            reg = self.reg_lambda * (proposed - 1.0)
            proposed -= reg
            
            # Change penalty
            change_penalty = self.change_lambda * abs(proposed - old_w)
            if proposed > old_w:
                proposed -= change_penalty
            else:
                proposed += change_penalty
            
            new_weights[tag] = round(max(0.1, min(3.0, proposed)), 4)
        
        profile.keyword_weights.update(new_weights)
        return new_weights


def _bucket_target(bucket: str) -> float:
    """Map bucket to target value for optimization."""
    return {
        "tools": 1.0,
        "interested": 0.5,
        "not_interested": -0.5,
        "ignored": -0.1,
    }.get(bucket, 0.0)
