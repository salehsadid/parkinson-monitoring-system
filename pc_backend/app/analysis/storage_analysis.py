"""
Storage analysis: database growth, 72-hour feasibility, projections.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class StorageAnalysis:
    total_rows: int
    database_size_bytes: int
    avg_bytes_per_row: float
    rows_per_second: float
    rows_per_minute: float
    rows_per_hour: float
    projected_rows_per_day: float
    projected_rows_per_72h: float
    projected_size_per_day_bytes: float
    projected_size_per_72h_bytes: float
    measured_duration_seconds: float
    declared_rate_hz: int


def analyze_storage(
    total_rows: int,
    database_size_bytes: int,
    duration_seconds: float,
    declared_rate_hz: int = 50,
) -> StorageAnalysis:
    """
    Compute storage metrics and projections.

    Args:
        total_rows: Number of SensorRecord rows
        database_size_bytes: SQLite file size in bytes
        duration_seconds: Time span of data in seconds
        declared_rate_hz: Configured sampling rate
    """
    if total_rows < 2 or duration_seconds <= 0:
        return StorageAnalysis(
            total_rows=total_rows,
            database_size_bytes=database_size_bytes,
            avg_bytes_per_row=0.0,
            rows_per_second=0.0,
            rows_per_minute=0.0,
            rows_per_hour=0.0,
            projected_rows_per_day=0.0,
            projected_rows_per_72h=0.0,
            projected_size_per_day_bytes=0.0,
            projected_size_per_72h_bytes=0.0,
            measured_duration_seconds=duration_seconds,
            declared_rate_hz=declared_rate_hz,
        )

    avg_bytes = database_size_bytes / total_rows
    rps = total_rows / duration_seconds
    rpm = rps * 60
    rph = rps * 3600

    rows_day = rph * 24
    rows_72h = rph * 72
    size_day = rows_day * avg_bytes
    size_72h = rows_72h * avg_bytes

    return StorageAnalysis(
        total_rows=total_rows,
        database_size_bytes=database_size_bytes,
        avg_bytes_per_row=round(avg_bytes, 2),
        rows_per_second=round(rps, 2),
        rows_per_minute=round(rpm, 2),
        rows_per_hour=round(rph, 2),
        projected_rows_per_day=round(rows_day, 0),
        projected_rows_per_72h=round(rows_72h, 0),
        projected_size_per_day_bytes=round(size_day, 0),
        projected_size_per_72h_bytes=round(size_72h, 0),
        measured_duration_seconds=round(duration_seconds, 2),
        declared_rate_hz=declared_rate_hz,
    )


def format_bytes(size_bytes: float) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
