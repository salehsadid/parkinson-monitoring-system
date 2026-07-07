"""
Data retention service for the Parkinson's Monitoring System.

This module implements the 72-hour rolling history policy for sensor
data. It provides utilities to clean up old records while preserving
event summaries.

Retention Policy:
- SensorRecord: Deleted after 72 hours (configurable)
- FOGEvent: Preserved (event summaries should be kept longer)
- TremorResult: Preserved (event summaries should be kept longer)
- Patient, Device: Preserved (metadata should be kept)

Future Considerations:
- Event summaries may need separate retention policy
- Archived data could be moved to cold storage
- Clinical data may require longer retention periods
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import delete
from sqlalchemy.orm import Session

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import SensorRecord

logger = logging.getLogger(__name__)


def cleanup_old_sensor_records(
    db: Session,
    retention_hours: Optional[int] = None,
    patient_id: Optional[str] = None,
) -> int:
    """
    Delete sensor records older than the retention period.

    This function implements the 72-hour rolling window policy.
    Only SensorRecord entries are deleted; event summaries are preserved.

    Args:
        db: Database session
        retention_hours: Optional override for retention period
        patient_id: Optional patient ID filter (for per-patient cleanup)

    Returns:
        int: Number of records deleted
    """
    hours = retention_hours or settings.RETENTION_HOURS
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    cutoff_ms = int(cutoff_time.timestamp() * 1000)

    # Build delete query
    stmt = delete(SensorRecord).where(SensorRecord.timestamp_ms < cutoff_ms)

    # Optional: filter by patient
    if patient_id:
        stmt = stmt.where(SensorRecord.patient_id == patient_id)

    # Execute deletion
    result = db.execute(stmt)
    deleted_count = result.rowcount
    db.commit()

    if deleted_count > 0:
        logger.info(
            f"Cleaned up {deleted_count} sensor records older than {hours} hours"
        )

    return deleted_count


def get_record_count(
    db: Session,
    patient_id: Optional[str] = None,
) -> int:
    """
    Get the current count of sensor records.

    Args:
        db: Database session
        patient_id: Optional patient ID filter

    Returns:
        int: Number of sensor records
    """
    from sqlalchemy import func

    query = db.query(func.count(SensorRecord.id))
    if patient_id:
        query = query.filter(SensorRecord.patient_id == patient_id)
    return query.scalar() or 0


def get_oldest_record_timestamp(
    db: Session,
    patient_id: Optional[str] = None,
) -> Optional[datetime]:
    """
    Get the timestamp of the oldest sensor record.

    Args:
        db: Database session
        patient_id: Optional patient ID filter

    Returns:
        Optional[datetime]: Oldest record timestamp, or None if no records
    """
    from sqlalchemy import func

    query = db.query(func.min(SensorRecord.timestamp_ms))
    if patient_id:
        query = query.filter(SensorRecord.patient_id == patient_id)
    min_ms = query.scalar()

    if min_ms is None:
        return None

    return datetime.fromtimestamp(min_ms / 1000.0)


def get_newest_record_timestamp(
    db: Session,
    patient_id: Optional[str] = None,
) -> Optional[datetime]:
    """
    Get the timestamp of the newest sensor record.

    Args:
        db: Database session
        patient_id: Optional patient ID filter

    Returns:
        Optional[datetime]: Newest record timestamp, or None if no records
    """
    from sqlalchemy import func

    query = db.query(func.max(SensorRecord.timestamp_ms))
    if patient_id:
        query = query.filter(SensorRecord.patient_id == patient_id)
    max_ms = query.scalar()

    if max_ms is None:
        return None

    return datetime.fromtimestamp(max_ms / 1000.0)


def get_retention_stats(
    db: Session,
    patient_id: Optional[str] = None,
) -> dict:
    """
    Get statistics about data retention.

    Args:
        db: Database session
        patient_id: Optional patient ID filter

    Returns:
        dict: Retention statistics including counts and time range
    """
    record_count = get_record_count(db, patient_id)
    oldest = get_oldest_record_timestamp(db, patient_id)
    newest = get_newest_record_timestamp(db, patient_id)

    stats = {
        "record_count": record_count,
        "retention_hours": settings.RETENTION_HOURS,
        "oldest_record": oldest.isoformat() if oldest else None,
        "newest_record": newest.isoformat() if newest else None,
    }

    if oldest and newest:
        time_span = newest - oldest
        stats["time_span_hours"] = time_span.total_seconds() / 3600

    return stats
