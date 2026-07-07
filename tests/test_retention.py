"""
Tests for 72-hour data retention.

This module tests the retention cleanup functionality for
sensor records.

Stage 1.1: Tests updated to include server_received_at_ms field.
"""

import time
from datetime import datetime, timedelta

import pytest

from pc_backend.app.database.base import SensorRecord
from pc_backend.app.database.retention import (
    cleanup_old_sensor_records,
    get_record_count,
    get_retention_stats,
)


def _create_sensor_record(db, timestamp_ms, patient_id="P001"):
    """Helper to create a sensor record with server_received_at_ms."""
    record = SensorRecord(
        patient_id=patient_id,
        device_id="ESP32_001",
        sequence=0,
        timestamp_ms=timestamp_ms,
        server_received_at_ms=int(time.time() * 1000),
        sampling_rate_hz=50,
        hand_ax=0.0, hand_ay=0.0, hand_az=9.8,
        hand_gx=0.0, hand_gy=0.0, hand_gz=0.0,
        shoe_ax=0.0, shoe_ay=0.0, shoe_az=9.8,
        shoe_gx=0.0, shoe_gy=0.0, shoe_gz=0.0,
    )
    db.add(record)
    db.commit()
    return record


def test_cleanup_old_records(test_db_session):
    """Test that old records are cleaned up."""
    # Create old record (100 hours ago)
    old_time = datetime.utcnow() - timedelta(hours=100)
    old_timestamp = int(old_time.timestamp() * 1000)
    _create_sensor_record(test_db_session, old_timestamp)

    # Create recent record (10 hours ago)
    recent_time = datetime.utcnow() - timedelta(hours=10)
    recent_timestamp = int(recent_time.timestamp() * 1000)
    _create_sensor_record(test_db_session, recent_timestamp)

    # Verify both records exist
    assert get_record_count(test_db_session) == 2

    # Run cleanup with 72-hour retention
    deleted_count = cleanup_old_sensor_records(test_db_session, retention_hours=72)

    # Verify old record was deleted
    assert deleted_count == 1
    assert get_record_count(test_db_session) == 1


def test_cleanup_no_records_to_delete(test_db_session):
    """Test cleanup when no records need to be deleted."""
    # Create recent record (10 hours ago)
    recent_time = datetime.utcnow() - timedelta(hours=10)
    recent_timestamp = int(recent_time.timestamp() * 1000)
    _create_sensor_record(test_db_session, recent_timestamp)

    # Run cleanup
    deleted_count = cleanup_old_sensor_records(test_db_session, retention_hours=72)

    # Verify no records were deleted
    assert deleted_count == 0
    assert get_record_count(test_db_session) == 1


def test_cleanup_empty_database(test_db_session):
    """Test cleanup on empty database."""
    deleted_count = cleanup_old_sensor_records(test_db_session, retention_hours=72)
    assert deleted_count == 0


def test_cleanup_by_patient(test_db_session):
    """Test cleanup filtered by patient."""
    # Create old records for different patients
    old_time = datetime.utcnow() - timedelta(hours=100)
    old_timestamp = int(old_time.timestamp() * 1000)

    _create_sensor_record(test_db_session, old_timestamp, patient_id="P001")
    _create_sensor_record(test_db_session, old_timestamp, patient_id="P002")

    # Cleanup only P001
    deleted_count = cleanup_old_sensor_records(
        test_db_session,
        retention_hours=72,
        patient_id="P001"
    )

    # Verify only P001 record was deleted
    assert deleted_count == 1
    count_p001 = get_record_count(test_db_session, patient_id="P001")
    count_p002 = get_record_count(test_db_session, patient_id="P002")
    assert count_p001 == 0
    assert count_p002 == 1


def test_retention_stats(test_db_session):
    """Test retention statistics."""
    # Create records
    now = datetime.utcnow()
    for hours_ago in [10, 20, 30]:
        timestamp = int((now - timedelta(hours=hours_ago)).timestamp() * 1000)
        _create_sensor_record(test_db_session, timestamp)

    stats = get_retention_stats(test_db_session)

    assert stats["record_count"] == 3
    assert stats["retention_hours"] == 72
    assert stats["oldest_record"] is not None
    assert stats["newest_record"] is not None
    assert "time_span_hours" in stats
