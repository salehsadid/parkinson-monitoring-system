"""
Signal quality analysis: baseline stats, noise, magnitude, independence checks.

All functions are pure — no database dependency.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import statistics
import math


@dataclass
class ChannelStats:
    count: int
    mean: float
    median: float
    std: float
    min_val: float
    max_val: float
    rms: float


@dataclass
class MagnitudeStats:
    channel: str
    count: int
    mean: float
    median: float
    std: float
    min_val: float
    max_val: float


@dataclass
class SignalQualityReport:
    hand_accel: Dict[str, ChannelStats]
    hand_gyro: Dict[str, ChannelStats]
    shoe_accel: Dict[str, ChannelStats]
    shoe_gyro: Dict[str, ChannelStats]
    hand_accel_magnitude: MagnitudeStats
    hand_gyro_magnitude: MagnitudeStats
    shoe_accel_magnitude: MagnitudeStats
    shoe_gyro_magnitude: MagnitudeStats
    hand_movement_energy: float
    shoe_movement_energy: float


HAND_ACCEL_CHANNELS = ["hand_ax", "hand_ay", "hand_az"]
HAND_GYRO_CHANNELS = ["hand_gx", "hand_gy", "hand_gz"]
SHOE_ACCEL_CHANNELS = ["shoe_ax", "shoe_ay", "shoe_az"]
SHOE_GYRO_CHANNELS = ["shoe_gx", "shoe_gy", "shoe_gz"]


def _channel_stats(values: List[float]) -> ChannelStats:
    if not values:
        return ChannelStats(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    mean_v = statistics.mean(values)
    squared = [v ** 2 for v in values]
    rms_val = math.sqrt(statistics.mean(squared))

    return ChannelStats(
        count=len(values),
        mean=round(mean_v, 6),
        median=round(statistics.median(values), 6),
        std=round(statistics.stdev(values), 6) if len(values) > 1 else 0.0,
        min_val=round(min(values), 6),
        max_val=round(max(values), 6),
        rms=round(rms_val, 6),
    )


def _compute_magnitude(ax: List[float], ay: List[float], az: List[float]) -> List[float]:
    return [math.sqrt(a ** 2 + b ** 2 + c ** 2) for a, b, c in zip(ax, ay, az)]


def _magnitude_stats(values: List[float], channel: str) -> MagnitudeStats:
    if not values:
        return MagnitudeStats(channel, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
    return MagnitudeStats(
        channel=channel,
        count=len(values),
        mean=round(statistics.mean(values), 6),
        median=round(statistics.median(values), 6),
        std=round(statistics.stdev(values), 6) if len(values) > 1 else 0.0,
        min_val=round(min(values), 6),
        max_val=round(max(values), 6),
    )


def compute_signal_quality(records: List[dict]) -> SignalQualityReport:
    """
    Compute comprehensive signal quality metrics from records.

    Each record must have all 12 IMU channel keys.
    """
    hand_ax = [r["hand_ax"] for r in records]
    hand_ay = [r["hand_ay"] for r in records]
    hand_az = [r["hand_az"] for r in records]
    hand_gx = [r["hand_gx"] for r in records]
    hand_gy = [r["hand_gy"] for r in records]
    hand_gz = [r["hand_gz"] for r in records]

    shoe_ax = [r["shoe_ax"] for r in records]
    shoe_ay = [r["shoe_ay"] for r in records]
    shoe_az = [r["shoe_az"] for r in records]
    shoe_gx = [r["shoe_gx"] for r in records]
    shoe_gy = [r["shoe_gy"] for r in records]
    shoe_gz = [r["shoe_gz"] for r in records]

    hand_accel = {ch: _channel_stats(vals) for ch, vals in
                  zip(["ax", "ay", "az"], [hand_ax, hand_ay, hand_az])}
    hand_gyro = {ch: _channel_stats(vals) for ch, vals in
                 zip(["gx", "gy", "gz"], [hand_gx, hand_gy, hand_gz])}
    shoe_accel = {ch: _channel_stats(vals) for ch, vals in
                  zip(["ax", "ay", "az"], [shoe_ax, shoe_ay, shoe_az])}
    shoe_gyro = {ch: _channel_stats(vals) for ch, vals in
                 zip(["gx", "gy", "gz"], [shoe_gx, shoe_gy, shoe_gz])}

    hand_accel_mag = _compute_magnitude(hand_ax, hand_ay, hand_az)
    hand_gyro_mag = _compute_magnitude(hand_gx, hand_gy, hand_gz)
    shoe_accel_mag = _compute_magnitude(shoe_ax, shoe_ay, shoe_az)
    shoe_gyro_mag = _compute_magnitude(shoe_gx, shoe_gy, shoe_gz)

    hand_energy = sum(v ** 2 for v in hand_accel_mag) / len(hand_accel_mag) if hand_accel_mag else 0.0
    shoe_energy = sum(v ** 2 for v in shoe_accel_mag) / len(shoe_accel_mag) if shoe_accel_mag else 0.0

    return SignalQualityReport(
        hand_accel=hand_accel,
        hand_gyro=hand_gyro,
        shoe_accel=shoe_accel,
        shoe_gyro=shoe_gyro,
        hand_accel_magnitude=_magnitude_stats(hand_accel_mag, "hand_accel"),
        hand_gyro_magnitude=_magnitude_stats(hand_gyro_mag, "hand_gyro"),
        shoe_accel_magnitude=_magnitude_stats(shoe_accel_mag, "shoe_accel"),
        shoe_gyro_magnitude=_magnitude_stats(shoe_gyro_mag, "shoe_gyro"),
        hand_movement_energy=round(hand_energy, 6),
        shoe_movement_energy=round(shoe_energy, 6),
    )


def check_independence(
    records_a_moved: List[dict],
    records_b_still: List[dict],
    label_a: str = "hand",
    label_b: str = "shoe",
) -> dict:
    """
    Check if moving sensor A while B is still produces independent streams.

    Returns variance ratio and energy ratio for evidence.
    """
    def _variance(vals):
        return statistics.variance(vals) if len(vals) > 1 else 0.0

    a_ax = [r[f"{label_a}_ax"] for r in records_a_moved]
    a_ay = [r[f"{label_a}_ay"] for r in records_a_moved]
    a_az = [r[f"{label_a}_az"] for r in records_a_moved]
    b_ax = [r[f"{label_b}_ax"] for r in records_b_still]
    b_ay = [r[f"{label_b}_ay"] for r in records_b_still]
    b_az = [r[f"{label_b}_az"] for r in records_b_still]

    a_var = _variance(a_ax) + _variance(a_ay) + _variance(a_az)
    b_var = _variance(b_ax) + _variance(b_ay) + _variance(b_az)

    a_energy = sum(ax ** 2 + ay ** 2 + az ** 2 for ax, ay, az in zip(a_ax, a_ay, a_az)) / max(len(a_ax), 1)
    b_energy = sum(ax ** 2 + ay ** 2 + az ** 2 for ax, ay, az in zip(b_ax, b_ay, b_az)) / max(len(b_ax), 1)

    return {
        "moved_sensor": label_a,
        "still_sensor": label_b,
        "moved_variance": round(a_var, 6),
        "still_variance": round(b_var, 6),
        "variance_ratio": round(a_var / b_var, 2) if b_var > 0 else float("inf"),
        "moved_energy": round(a_energy, 6),
        "still_energy": round(b_energy, 6),
        "energy_ratio": round(a_energy / b_energy, 2) if b_energy > 0 else float("inf"),
        "evidence": "independent" if a_var > b_var * 2 else "potentially_coupled",
    }
