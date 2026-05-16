"""Fast loop updater — per-save EMA update in latent space."""

from __future__ import annotations

import numpy as np

from muse.models import EngagementEvent, UserProfile, normalize_vector

# Learning rates per bucket (eta values)
BUCKET_ETA = {
    "tools": 0.05,
    "interested": 0.02,
    "not_interested": -0.03,
    "ignored": 0.0,
}

# Weight multipliers per bucket (for keyword slow loop)
BUCKET_WEIGHT_DELTA = {
    "tools": 1.15,
    "interested": 1.05,
    "not_interested": 0.90,
    "ignored": 0.995,
}

# Clamping
WEIGHT_MIN = 0.1
WEIGHT_MAX = 3.0


class FastLoopUpdater:
    """Update interest vector via exponential moving average."""

    def update_vector(
        self,
        profile: UserProfile,
        events: list[EngagementEvent],
    ) -> tuple[np.ndarray, float]:
        """
        Apply EMA update for each engagement event.
        
        Returns:
            (new_vector, delta) where delta is the L2 distance from old vector
        """
        vec = profile.vector().copy()
        old_vec = vec.copy()
        
        for event in events:
            eta = BUCKET_ETA.get(event.bucket, 0.0)
            if eta == 0.0:
                continue
            
            item_emb = np.array(event.item_embedding, dtype=np.float32)
            # EMA step: vec = vec + eta * (target - vec)
            vec += eta * (item_emb - vec)
        
        # Normalize to unit length
        vec = normalize_vector(vec)
        
        # Compute delta
        delta = float(np.linalg.norm(vec - old_vec))
        
        profile.set_vector(vec)
        return vec, delta

    def update_topic_weights(
        self,
        profile: UserProfile,
        events: list[EngagementEvent],
    ) -> None:
        """
        Update keyword weights based on bucket signals.
        This feeds data into the slow loop's keyword weight table.
        """
        for event in events:
            delta = BUCKET_WEIGHT_DELTA.get(event.bucket, 1.0)
            top_tag = event.top_tag
            
            current = profile.keyword_weights.get(top_tag, 1.0)
            new_weight = current * delta
            new_weight = max(WEIGHT_MIN, min(WEIGHT_MAX, new_weight))
            profile.keyword_weights[top_tag] = round(new_weight, 4)
