"""
Tests for Stage 2.1 analysis modules.
"""

import math
import pytest
from pc_backend.app.analysis.stream_quality import (
    compute_sampling_metrics,
    detect_sequence_gaps,
    compute_jitter_metrics,
    detect_sessions,
    compute_arrival_offset,
)
from pc_backend.app.analysis.signal_quality import (
    compute_signal_quality,
    check_independence,
)
from pc_backend.app.analysis.storage_analysis import (
    analyze_storage,
    format_bytes,
)


def _make_record(seq, ts, server_ts, **extra):
    base = {
        "sequence": seq,
        "timestamp_ms": ts,
        "server_received_at_ms": server_ts,
        "hand_ax": 0.0, "hand_ay": 0.0, "hand_az": 9.8,
        "hand_gx": 0.0, "hand_gy": 0.0, "hand_gz": 0.0,
        "shoe_ax": 0.0, "shoe_ay": 0.0, "shoe_az": 9.8,
        "shoe_gx": 0.0, "shoe_gy": 0.0, "shoe_gz": 0.0,
    }
    base.update(extra)
    return base


class TestSamplingMetrics:
    def test_empty_input(self):
        m = compute_sampling_metrics([])
        assert m.record_count == 0

    def test_single_record(self):
        m = compute_sampling_metrics([_make_record(0, 1000, 1000)])
        assert m.record_count == 1

    def test_normal_50hz(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(100)]
        m = compute_sampling_metrics(records)
        assert m.record_count == 100
        assert m.mean_interval_ms == 20.0
        assert m.observed_device_rate_hz == 50.0

    def test_observed_rate_matches(self):
        records = [_make_record(i, 1000 + i * 50, 1000 + i * 50) for i in range(50)]
        m = compute_sampling_metrics(records)
        assert m.observed_device_rate_hz == 20.0

    def test_p95_p99_computed(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(100)]
        m = compute_sampling_metrics(records)
        assert m.p95_interval_ms >= m.mean_interval_ms
        assert m.p99_interval_ms >= m.p95_interval_ms


class TestSequenceGaps:
    def test_empty_input(self):
        g = detect_sequence_gaps([])
        assert g.received_count == 0

    def test_continuous_sequence(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(100)]
        g = detect_sequence_gaps(records)
        assert g.missing_count == 0
        assert g.duplicate_count == 0
        assert g.estimated_loss_pct == 0.0

    def test_missing_sequence(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20)
                   for i in range(100) if i != 50]
        g = detect_sequence_gaps(records)
        assert g.missing_count >= 1
        assert g.estimated_loss_pct > 0

    def test_duplicate_sequence(self):
        records = [_make_record(5, 1000, 1000), _make_record(5, 1020, 1020)]
        g = detect_sequence_gaps(records)
        assert g.duplicate_count == 1

    def test_reset_detection(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(50)]
        records.append(_make_record(0, 2000, 2000))
        g = detect_sequence_gaps(records, reset_threshold=10)
        assert g.reset_detected is True


class TestJitter:
    def test_empty_input(self):
        j = compute_jitter_metrics([])
        assert j.mean_delta_ms == 0.0

    def test_constant_interval(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(50)]
        j = compute_jitter_metrics(records)
        assert j.mean_delta_ms == 20.0
        assert j.std_delta_ms == 0.0

    def test_jitter_computed(self):
        records = [_make_record(i, 1000 + i * 20 + (i % 3), 1000 + i * 20) for i in range(50)]
        j = compute_jitter_metrics(records)
        assert j.std_delta_ms >= 0
        assert j.p95_delta_ms >= j.mean_delta_ms


class TestSessions:
    def test_empty_input(self):
        s = detect_sessions([])
        assert len(s) == 0

    def test_single_session(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(100)]
        s = detect_sessions(records)
        assert len(s) == 1
        assert s[0].record_count == 100

    def test_gap_creates_session(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(50)]
        records.append(_make_record(50, 100000, 100000))
        s = detect_sessions(records)
        assert len(s) == 2

    def test_reset_creates_session(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(50)]
        records.append(_make_record(0, 2000, 2000))
        s = detect_sessions(records, reset_threshold=10)
        assert len(s) == 2


class TestArrivalOffset:
    def test_empty_input(self):
        o = compute_arrival_offset([])
        assert o["count"] == 0

    def test_constant_offset(self):
        records = [_make_record(i, 1000, 2000) for i in range(10)]
        o = compute_arrival_offset(records)
        assert o["mean_ms"] == 1000.0
        assert o["std_ms"] == 0.0


class TestSignalQuality:
    def test_empty_input(self):
        q = compute_signal_quality([])
        assert q.hand_accel["ax"].count == 0

    def test_gravity_detect(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20, hand_az=9.8) for i in range(100)]
        q = compute_signal_quality(records)
        assert abs(q.hand_accel["az"].mean - 9.8) < 0.01
        assert q.hand_accel_magnitude.mean > 9.0

    def test_energy_computed(self):
        records = [_make_record(i, 1000 + i * 20, 1000 + i * 20, hand_az=9.8) for i in range(10)]
        q = compute_signal_quality(records)
        assert q.hand_movement_energy > 0


class TestIndependence:
    def test_moved_vs_still(self):
        moved = [_make_record(i, 1000 + i * 20, 1000 + i * 20,
                              hand_ax=i * 0.5, hand_ay=i * 0.3, hand_az=9.8)
                 for i in range(100)]
        still = [_make_record(i, 1000 + i * 20, 1000 + i * 20) for i in range(100)]
        result = check_independence(moved, still, "hand", "shoe")
        assert result["variance_ratio"] > 1
        assert result["evidence"] == "independent"


class TestStorageAnalysis:
    def test_empty_input(self):
        s = analyze_storage(0, 0, 0)
        assert s.total_rows == 0

    def test_projections(self):
        s = analyze_storage(1000, 200000, 20.0, 50)
        assert s.rows_per_second == 50.0
        assert s.projected_rows_per_day > 0

    def test_format_bytes(self):
        assert "KB" in format_bytes(1500)
        assert "MB" in format_bytes(1500000)
        assert "GB" in format_bytes(1500000000)
