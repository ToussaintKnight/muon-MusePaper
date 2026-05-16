#!/usr/bin/env python3
"""
Daily Effectiveness Metrics — Muse User Performance Tracker

Computes once per day (after the evening save) to measure:
  • How effectively the user interacts with Muse
  • Time efficiency (especially for high-pace / OPC users)
  • Self / business growth signals

All formulas are pure functions over the day's engagement history.
No ML training required.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
import math


# ── Constants ──────────────────────────────────────────────────────────

# Bucket eta values (must match fast_loop.py)
BUCKET_ETA = {
    "tools": 0.05,
    "interested": 0.02,
    "not_interested": -0.03,
    "ignored": 0.0,
}

# Reference values for normalization (calibrated for high-pace users)
REF_DECISION_VELOCITY = 12.0      # cards per minute (target for OPCers)
REF_SNR = 4.0                     # signal-to-noise ratio target
REF_STACK_VELOCITY = 3.0          # new tools per week target
REF_COVERAGE_EFF = 0.6            # 60% source diversity engagement


# ── Data Model ─────────────────────────────────────────────────────────

@dataclass
class DailyMetrics:
    """Computed once per day, persisted to profile.json."""
    date: str                       # ISO date
    
    # ── Core Engagement ──
    cards_presented: int            # total items shown today
    cards_interacted: int           # dragged to any bucket
    cards_ignored: int              # left in inbox
    
    # ── Effectiveness (high-pace / OPC focus) ──
    decision_velocity: float        # cards processed per minute
    actionability_index: float      # tools / (tools + interested)
    signal_to_noise: float          # (tools + interested) / max(1, not_interested)
    coverage_efficiency: float      # unique sources engaged / unique sources shown
    
    # ── Growth Signals ──
    stack_velocity_week: int        # tools synced to Notion this week
    interest_stability: float       # cosine(yesterday_vec, today_vec)
    interest_drift_direction: str   # "focusing" | "exploring" | "stable"
    
    # ── Time ──
    session_time_min: float         # active time in Kanban (estimated)
    time_to_first_action_sec: float # latency from open to first drag
    
    # ── Composite Score ──
    daily_effectiveness_score: float  # 0-100 composite
    
    # ── Interpretation ──
    summary: str                    # one-line human-readable summary


# ── Formula Implementations ────────────────────────────────────────────

def decision_velocity(cards_interacted: int, session_time_min: float) -> float:
    """
    How many cards the user processes per minute.
    
    High-pace OPCers target: > 10 cards/min
    Typical user: 3-6 cards/min
    """
    if session_time_min <= 0:
        return 0.0
    return cards_interacted / session_time_min


def actionability_index(tools: int, interested: int) -> float:
    """
    Of the content the user cares about, how much is *actionable*
    (Tools) vs just *interesting* (Interested).
    
    Business growth signal: high AI = user is actively building their stack.
    """
    total = tools + interested
    if total == 0:
        return 0.0
    return tools / total


def signal_to_noise(tools: int, interested: int, not_interested: int) -> float:
    """
    Ratio of positive signals to negative signals.
    
    SNR > 3  → Muse is well-tuned to this user
    SNR 1-3  → Normal, still learning
    SNR < 1  → Content mismatch, vector may need reset
    """
    positive = tools + interested
    negative = max(1, not_interested)
    return positive / negative


def coverage_efficiency(sources_engaged: set[str], sources_shown: set[str]) -> float:
    """
    What fraction of presented sources did the user actually engage with?
    
    Low  (~0.2) → user is hyper-focused on 1-2 domains
    High (~0.8) → user is exploring broadly
    Both are valid; trend matters more than absolute.
    """
    if not sources_shown:
        return 0.0
    return len(sources_engaged) / len(sources_shown)


def interest_stability(yesterday_vector: list[float], today_vector: list[float]) -> float:
    """
    Cosine similarity between yesterday's and today's interest vector.
    
    0.95-1.00 → stable interests (mature profile)
    0.80-0.95 → moderate drift (normal learning)
    0.60-0.80 → rapid shift (new interests emerging)
    < 0.60    → volatile, may need onboarding reset
    """
    def _dot(a, b):
        return sum(x * y for x, y in zip(a, b))
    
    def _norm(v):
        return math.sqrt(sum(x * x for x in v))
    
    dot = _dot(yesterday_vector, today_vector)
    norm_a = _norm(yesterday_vector)
    norm_b = _norm(today_vector)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def interest_drift_direction(stability: float, 
                              yesterday_top_tags: list[str],
                              today_top_tags: list[str]) -> str:
    """
    Classify the nature of interest drift.
    """
    if stability > 0.95:
        return "stable"
    
    # Count how many top tags changed
    common = set(yesterday_top_tags) & set(today_top_tags)
    if len(common) >= 3:
        return "focusing"      # same tags, vector sharpening
    else:
        return "exploring"     # new tags entering top-5


def session_time_estimate(cards_interacted: int, 
                          cards_ignored: int,
                          avg_drag_time_sec: float = 3.0) -> float:
    """
    Estimate active Kanban time in minutes.
    
    Assumes:
      - each drag takes ~3 seconds (read + decide + drag)
      - ignored cards add ~1 second of scanning each
      - fixed overhead of 30s for opening/saving
    """
    drag_time = cards_interacted * avg_drag_time_sec
    scan_time = cards_ignored * 1.0
    overhead = 30.0
    total_sec = drag_time + scan_time + overhead
    return total_sec / 60.0


def daily_effectiveness_score(
    dv: float,
    ai: float,
    snr: float,
    sv_week: int,
    stability: float,
    coverage_eff: float,
) -> float:
    """
    Composite score 0-100 measuring overall daily effectiveness.
    
    Weights calibrated for OPC / high-pace builders:
      - Decision velocity matters (quick triage)
      - Actionability matters (building, not just browsing)
      - Signal quality matters (relevant content)
      - Stack growth matters (tangible output)
    """
    # Normalize each dimension to 0-1
    dv_norm = min(dv / REF_DECISION_VELOCITY, 1.0)
    snr_norm = min(snr / REF_SNR, 1.0)
    sv_norm = min(sv_week / REF_STACK_VELOCITY, 1.0)
    
    # Stability: inverted-U curve
    #   Too stable (0.99) = stagnating
    #   Too volatile (0.5) = unfocused
    #   Sweet spot (0.85) = learning but focused
    stability_score = 1.0 - abs(stability - 0.85) / 0.15
    stability_score = max(0.0, min(1.0, stability_score))
    
    score = (
        0.20 * dv_norm +          # speed of decision-making
        0.25 * ai +               # actionability (tools vs browse)
        0.20 * snr_norm +         # content relevance
        0.20 * sv_norm +          # tangible stack growth
        0.10 * stability_score +  # healthy learning rate
        0.05 * coverage_eff       # exploration balance
    )
    
    return round(score * 100, 1)


def generate_summary(m: DailyMetrics) -> str:
    """One-line human-readable summary."""
    parts = []
    
    if m.daily_effectiveness_score >= 80:
        parts.append("[HIGH] High-effectiveness session")
    elif m.daily_effectiveness_score >= 60:
        parts.append("[SOLID] Solid session")
    elif m.daily_effectiveness_score >= 40:
        parts.append("[MODERATE] Moderate session")
    else:
        parts.append("[LOW] Low-engagement session")
    
    parts.append(f"-- {m.cards_interacted}/{m.cards_presented} cards")
    parts.append(f"at {m.decision_velocity:.1f}/min")
    
    if m.stack_velocity_week > 0:
        parts.append(f"| {m.stack_velocity_week} tools this week")
    
    parts.append(f"| interests {m.interest_drift_direction}")
    
    return " ".join(parts)


# ── Main Entry Point ───────────────────────────────────────────────────

def compute_daily_metrics(
    today_events: list[dict],
    yesterday_vector: Optional[list[float]],
    today_vector: list[float],
    yesterday_top_tags: list[str],
    today_top_tags: list[str],
    notion_tools_this_week: int,
) -> DailyMetrics:
    """
    Compute all daily metrics from raw session data.
    
    Args:
        today_events: list of {"item_id", "bucket", "source", "timestamp"}
        yesterday_vector: previous day's interest vector (None on day 1)
        today_vector: current interest vector
        yesterday_top_tags: top-5 tag names from yesterday
        today_top_tags: top-5 tag names from today
        notion_tools_this_week: count of tools synced to Notion in last 7 days
    """
    # Count buckets
    buckets = {"tools": 0, "interested": 0, "not_interested": 0, "ignored": 0}
    sources_engaged = set()
    sources_shown = set()
    
    for ev in today_events:
        b = ev.get("bucket", "ignored")
        buckets[b] = buckets.get(b, 0) + 1
        sources_shown.add(ev.get("source", "unknown"))
        if b != "ignored":
            sources_engaged.add(ev.get("source", "unknown"))
    
    cards_interacted = buckets["tools"] + buckets["interested"] + buckets["not_interested"]
    cards_ignored = buckets["ignored"]
    cards_presented = cards_interacted + cards_ignored
    
    # Time estimates
    session_time = session_time_estimate(cards_interacted, cards_ignored)
    
    # Core metrics
    dv = decision_velocity(cards_interacted, session_time)
    ai = actionability_index(buckets["tools"], buckets["interested"])
    snr = signal_to_noise(buckets["tools"], buckets["interested"], buckets["not_interested"])
    ce = coverage_efficiency(sources_engaged, sources_shown)
    
    # Vector metrics
    if yesterday_vector:
        stability = interest_stability(yesterday_vector, today_vector)
    else:
        stability = 1.0  # first day, perfectly "stable" by definition
    
    drift = interest_drift_direction(stability, yesterday_top_tags, today_top_tags)
    
    # Composite
    score = daily_effectiveness_score(dv, ai, snr, notion_tools_this_week, stability, ce)
    
    m = DailyMetrics(
        date=datetime.now().strftime("%Y-%m-%d"),
        cards_presented=cards_presented,
        cards_interacted=cards_interacted,
        cards_ignored=cards_ignored,
        decision_velocity=round(dv, 1),
        actionability_index=round(ai, 2),
        signal_to_noise=round(snr, 2),
        coverage_efficiency=round(ce, 2),
        stack_velocity_week=notion_tools_this_week,
        interest_stability=round(stability, 3),
        interest_drift_direction=drift,
        session_time_min=round(session_time, 1),
        time_to_first_action_sec=0.0,  # requires frontend instrumentation
        daily_effectiveness_score=score,
        summary="",
    )
    m.summary = generate_summary(m)
    return m


# ── Demo ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Simulate a high-pace OPC user session
    events = []
    
    # 50 items presented
    # User drags: 8 Tools, 12 Interested, 5 Not Interested, 25 Ignored
    for i in range(8):
        events.append({"bucket": "tools", "source": "rsshub_hn"})
    for i in range(12):
        events.append({"bucket": "interested", "source": "newsnow_zhihu"})
    for i in range(5):
        events.append({"bucket": "not_interested", "source": "newsnow_weibo"})
    for i in range(25):
        events.append({"bucket": "ignored", "source": "rsshub_github"})
    
    yesterday_vec = [0.1] * 256
    today_vec = [0.12] * 256
    
    m = compute_daily_metrics(
        today_events=events,
        yesterday_vector=yesterday_vec,
        today_vector=today_vec,
        yesterday_top_tags=["AI/ML", "Tools", "Design"],
        today_top_tags=["AI/ML", "Tools", "Design", "Startup"],
        notion_tools_this_week=4,
    )
    
    print("=" * 60)
    print("MUSE DAILY EFFECTIVENESS REPORT")
    print("=" * 60)
    for k, v in m.__dict__.items():
        print(f"  {k:30s}: {v}")
