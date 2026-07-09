"""
Stream quality analysis: sampling rate, packet loss, jitter, session segmentation.

All functions operate on lists of dicts or tuples from database queries.
No database dependency in pure functions.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import statistics
import math


@dataclass
class SamplingMetrics:
    declared_rate_hz: int
    record_count: int
    duration_ms: float
    observed_device_rate_hz: float
    observed_server_rate_hz: float
    mean_interval_ms: float
    median_interval_ms: float
    min_interval_ms: float
    max_interval_ms: float
    std_interval_ms: float
    p95_interval_ms: float
    p99_interval_ms: float


@dataclass
class SequenceGapAnalysis:
    first_sequence: int
    last_sequence: int
    received_count: int
    expected_count: int
    missing_count: int
    gap_count: int
    duplicate_count: int
    out_of_order_count: int
    estimated_loss_pct: float
    reset_detected: bool
    gaps: List[int] = field(default_factory=list)


@dataclass
class JitterMetrics:
    expected_interval_ms: float
    mean_delta_ms: float
    median_delta_ms: float
    std_delta_ms: float
    min_delta_ms: float
    max_delta_ms: float
    p95_delta_ms: float
    p99_delta_ms: float
    mean_absolute_deviation_ms: float


@dataclass
class SessionBoundary:
    start_index: int
    end_index: int
    start_timestamp_ms: int
    end_timestamp_ms: int
    record_count: int
    gap_before_ms: float
    reason: str


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)


def compute_sampling_metrics(
    records: List[dict],
    declared_rate_hz: int = 50,
) -> SamplingMetrics:
    """
    Compute sampling rate metrics from ordered records.

    Each record must have 'timestamp_ms' and 'server_received_at_ms'.
    """
    if len(records) < 2:
        return SamplingMetrics(
            declared_rate_hz=declared_rate_hz,
            record_count=len(records),
            duration_ms=0.0,
            observed_device_rate_hz=0.0,
            observed_server_rate_hz=0.0,
            mean_interval_ms=0.0,
            median_interval_ms=0.0,
            min_interval_ms=0.0,
            max_interval_ms=0.0,
            std_interval_ms=0.0,
            p95_interval_ms=0.0,
            p99_interval_ms=0.0,
        )

    device_intervals = []
    server_intervals = []

    for i in range(1, len(records)):
        dt = records[i]["timestamp_ms"] - records[i - 1]["timestamp_ms"]
        ds = records[i]["server_received_at_ms"] - records[i - 1]["server_received_at_ms"]
        if dt > 0:
            device_intervals.append(float(dt))
        if ds > 0:
            server_intervals.append(float(ds))

    if not device_intervals:
        device_intervals = [0.0]
    if not server_intervals:
        server_intervals = [0.0]

    sorted_di = sorted(device_intervals)
    sorted_si = sorted(server_intervals)

    duration_ms = float(records[-1]["timestamp_ms"] - records[0]["timestamp_ms"])

    dev_rate = 1000.0 / statistics.mean(device_intervals) if device_intervals else 0.0
    srv_rate = 1000.0 / statistics.mean(server_intervals) if server_intervals else 0.0

    return SamplingMetrics(
        declared_rate_hz=declared_rate_hz,
        record_count=len(records),
        duration_ms=duration_ms,
        observed_device_rate_hz=round(dev_rate, 2),
        observed_server_rate_hz=round(srv_rate, 2),
        mean_interval_ms=round(statistics.mean(device_intervals), 2),
        median_interval_ms=round(statistics.median(device_intervals), 2),
        min_interval_ms=round(min(device_intervals), 2),
        max_interval_ms=round(max(device_intervals), 2),
        std_interval_ms=round(statistics.stdev(device_intervals), 2) if len(device_intervals) > 1 else 0.0,
        p95_interval_ms=round(_percentile(sorted_di, 95), 2),
        p99_interval_ms=round(_percentile(sorted_di, 99), 2),
    )


def detect_sequence_gaps(
    records: List[dict],
    reset_threshold: int = 1000,
) -> SequenceGapAnalysis:
    """
    Analyze sequence continuity.

    Detects gaps, duplicates, out-of-order, and resets.
    Reset detected when sequence decreases by more than reset_threshold.
    """
    if not records:
        return SequenceGapAnalysis(
            first_sequence=0, last_sequence=0, received_count=0,
            expected_count=0, missing_count=0, gap_count=0,
            duplicate_count=0, out_of_order_count=0,
            estimated_loss_pct=0.0, reset_detected=False,
        )

    sequences = [r["sequence"] for r in records]
    first_seq = sequences[0]
    last_seq = sequences[-1]
    received = len(sequences)

    gaps = []
    duplicates = 0
    out_of_order = 0
    reset_detected = False

    seen = set()
    for i, seq in enumerate(sequences):
        if seq in seen:
            duplicates += 1
        seen.add(seq)

        if i > 0:
            if seq < sequences[i - 1]:
                if sequences[i - 1] - seq > reset_threshold:
                    reset_detected = True
                else:
                    out_of_order += 1

    sorted_unique = sorted(set(sequences))
    for i in range(1, len(sorted_unique)):
        gap = sorted_unique[i] - sorted_unique[i - 1] - 1
        if gap > 0:
            gaps.extend(range(sorted_unique[i - 1] + 1, sorted_unique[i]))

    missing = len(gaps)
    expected = last_seq - first_seq + 1 if last_seq >= first_seq else 0
    loss_pct = (missing / expected * 100) if expected > 0 else 0.0

    return SequenceGapAnalysis(
        first_sequence=first_seq,
        last_sequence=last_seq,
        received_count=received,
        expected_count=expected,
        missing_count=missing,
        gap_count=len(gaps),
        duplicate_count=duplicates,
        out_of_order_count=out_of_order,
        estimated_loss_pct=round(loss_pct, 4),
        reset_detected=reset_detected,
        gaps=gaps[:100],  # limit for memory
    )


def compute_jitter_metrics(
    records: List[dict],
    use_server_timestamps: bool = False,
) -> JitterMetrics:
    """
    Compute timing jitter from consecutive records.

    Args:
        records: Ordered list of dicts with timestamp_ms and server_received_at_ms
        use_server_timestamps: If True, analyze server arrival times instead of device times
    """
    key = "server_received_at_ms" if use_server_timestamps else "timestamp_ms"

    if len(records) < 2:
        return JitterMetrics(
            expected_interval_ms=20.0, mean_delta_ms=0.0, median_delta_ms=0.0,
            std_delta_ms=0.0, min_delta_ms=0.0, max_delta_ms=0.0,
            p95_delta_ms=0.0, p99_delta_ms=0.0, mean_absolute_deviation_ms=0.0,
        )

    deltas = []
    for i in range(1, len(records)):
        d = float(records[i][key] - records[i - 1][key])
        if d > 0:
            deltas.append(d)

    if not deltas:
        return JitterMetrics(
            expected_interval_ms=20.0, mean_delta_ms=0.0, median_delta_ms=0.0,
            std_delta_ms=0.0, min_delta_ms=0.0, max_delta_ms=0.0,
            p95_delta_ms=0.0, p99_delta_ms=0.0, mean_absolute_deviation_ms=0.0,
        )

    sorted_deltas = sorted(deltas)
    mean_d = statistics.mean(deltas)
    mad = statistics.mean([abs(d - mean_d) for d in deltas])

    return JitterMetrics(
        expected_interval_ms=round(1000.0 / 50.0, 2),
        mean_delta_ms=round(mean_d, 2),
        median_delta_ms=round(statistics.median(deltas), 2),
        std_delta_ms=round(statistics.stdev(deltas), 2) if len(deltas) > 1 else 0.0,
        min_delta_ms=round(min(deltas), 2),
        max_delta_ms=round(max(deltas), 2),
        p95_delta_ms=round(_percentile(sorted_deltas, 95), 2),
        p99_delta_ms=round(_percentile(sorted_deltas, 99), 2),
        mean_absolute_deviation_ms=round(mad, 2),
    )


def detect_sessions(
    records: List[dict],
    gap_threshold_ms: float = 5000.0,
    reset_threshold: int = 1000,
) -> List[SessionBoundary]:
    """
    Segment records into sessions based on gaps and resets.

    A new session starts when:
    - Time gap exceeds gap_threshold_ms, or
    - Sequence decreases by more than reset_threshold
    """
    if not records:
        return []

    sessions = []
    session_start = 0

    for i in range(1, len(records)):
        time_gap = float(records[i]["timestamp_ms"] - records[i - 1]["timestamp_ms"])
        seq_drop = records[i - 1]["sequence"] - records[i]["sequence"]

        new_session = False
        reason = ""

        if time_gap > gap_threshold_ms:
            new_session = True
            reason = f"time_gap_{time_gap:.0f}ms"
        elif seq_drop > reset_threshold:
            new_session = True
            reason = f"sequence_reset_{seq_drop}"

        if new_session:
            sessions.append(SessionBoundary(
                start_index=session_start,
                end_index=i - 1,
                start_timestamp_ms=records[session_start]["timestamp_ms"],
                end_timestamp_ms=records[i - 1]["timestamp_ms"],
                record_count=i - session_start,
                gap_before_ms=time_gap,
                reason=reason,
            ))
            session_start = i

    sessions.append(SessionBoundary(
        start_index=session_start,
        end_index=len(records) - 1,
        start_timestamp_ms=records[session_start]["timestamp_ms"],
        end_timestamp_ms=records[-1]["timestamp_ms"],
        record_count=len(records) - session_start,
        gap_before_ms=0.0,
        reason="start" if session_start == 0 else "continuation",
    ))

    return sessions


def compute_arrival_offset(
    records: List[dict],
) -> dict:
    """
    Analyze device-vs-server timestamp offset.

    Note: offset includes device clock offset, network latency, processing delay.
    NOT pure network latency unless clocks are synchronized.
    """
    if not records:
        return {"mean_ms": 0, "std_ms": 0, "min_ms": 0, "max_ms": 0, "count": 0}

    offsets = [
        float(r["server_received_at_ms"] - r["timestamp_ms"])
        for r in records
    ]

    return {
        "mean_ms": round(statistics.mean(offsets), 2),
        "std_ms": round(statistics.stdev(offsets), 2) if len(offsets) > 1 else 0.0,
        "min_ms": round(min(offsets), 2),
        "max_ms": round(max(offsets), 2),
        "count": len(offsets),
    }
