"""Tests for effectiveness metrics."""

from muse.effectiveness import (
    decision_velocity,
    actionability_index,
    signal_to_noise,
    coverage_efficiency,
    interest_stability,
    daily_effectiveness_score,
    compute_daily_metrics,
)


class TestDecisionVelocity:
    def test_typical(self):
        assert decision_velocity(25, 2.5) == 10.0

    def test_zero_time(self):
        assert decision_velocity(10, 0) == 0.0


class TestActionabilityIndex:
    def test_all_tools(self):
        assert actionability_index(5, 0) == 1.0

    def test_half(self):
        assert actionability_index(3, 3) == 0.5

    def test_zero(self):
        assert actionability_index(0, 0) == 0.0


class TestSignalToNoise:
    def test_perfect(self):
        assert signal_to_noise(5, 5, 0) == 10.0

    def test_equal(self):
        assert signal_to_noise(2, 2, 4) == 1.0

    def test_no_negative(self):
        assert signal_to_noise(0, 0, 0) == 0.0


class TestCoverageEfficiency:
    def test_full(self):
        assert coverage_efficiency({"a", "b"}, {"a", "b"}) == 1.0

    def test_half(self):
        assert coverage_efficiency({"a"}, {"a", "b"}) == 0.5

    def test_empty(self):
        assert coverage_efficiency(set(), {"a"}) == 0.0


class TestInterestStability:
    def test_identical(self):
        v = [0.1] * 256
        assert interest_stability(v, v) == 1.0

    def test_orthogonal(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert interest_stability(a, b) == 0.0

    def test_zero_vector(self):
        assert interest_stability([0.0, 0.0], [1.0, 0.0]) == 0.0


class TestDailyEffectivenessScore:
    def test_perfect(self):
        score = daily_effectiveness_score(
            dv=15.0, ai=0.8, snr=5.0, sv_week=5, stability=0.85, coverage_eff=0.7
        )
        assert 80 <= score <= 100

    def test_poor(self):
        score = daily_effectiveness_score(
            dv=1.0, ai=0.1, snr=0.5, sv_week=0, stability=0.99, coverage_eff=0.1
        )
        assert score < 50


class TestComputeDailyMetrics:
    def test_basic_session(self):
        events = []
        for i in range(5):
            events.append({"bucket": "tools", "source": "a"})
        for i in range(10):
            events.append({"bucket": "interested", "source": "b"})
        for i in range(3):
            events.append({"bucket": "not_interested", "source": "c"})
        for i in range(32):
            events.append({"bucket": "ignored", "source": "d"})

        m = compute_daily_metrics(
            today_events=events,
            yesterday_vector=None,
            today_vector=[0.1] * 256,
            yesterday_top_tags=["a"],
            today_top_tags=["a", "b"],
            notion_tools_this_week=3,
        )

        assert m.cards_presented == 50
        assert m.cards_interacted == 18
        assert m.decision_velocity > 0
        assert 0 <= m.daily_effectiveness_score <= 100
        assert m.summary != ""
