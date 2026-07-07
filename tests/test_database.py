"""
Tests for database operations.

This module tests database initialization, model creation, and
basic CRUD operations.

Stage 1.1: Tests updated to include server_received_at_ms field.
"""

import time
import pytest
from datetime import datetime, timedelta

from pc_backend.app.database.base import (
    Base,
    Patient,
    Device,
    SensorRecord,
    FOGEvent,
    TremorResult,
    init_database,
)
from pc_backend.app.database.retention import (
    cleanup_old_sensor_records,
    get_record_count,
    get_retention_stats,
)


def test_database_initialization(test_db_engine):
    """Test database tables are created correctly."""
    # Tables should already be created by test_db_engine fixture
    from sqlalchemy import inspect
    inspector = inspect(test_db_engine)
    table_names = inspector.get_table_names()

    assert "patients" in table_names
    assert "devices" in table_names
    assert "sensor_records" in table_names
    assert "fog_events" in table_names
    assert "tremor_results" in table_names


def test_patient_creation(test_db_session):
    """Test patient record creation."""
    patient = Patient(patient_id="P001")
    test_db_session.add(patient)
    test_db_session.commit()

    retrieved = test_db_session.query(Patient).filter_by(patient_id="P001").first()
    assert retrieved is not None
    assert retrieved.patient_id == "P001"
    assert retrieved.created_at is not None


def test_device_creation(test_db_session):
    """Test device record creation."""
    device = Device(device_id="ESP32_001", patient_id="P001")
    test_db_session.add(device)
    test_db_session.commit()

    retrieved = test_db_session.query(Device).filter_by(device_id="ESP32_001").first()
    assert retrieved is not None
    assert retrieved.device_id == "ESP32_001"
    assert retrieved.patient_id == "P001"
    assert retrieved.created_at is not None
    assert retrieved.last_seen_at is not None


def test_sensor_record_creation(test_db_session):
    """Test sensor record creation with server_received_at_ms."""
    record = SensorRecord(
        patient_id="P001",
        device_id="ESP32_001",
        sequence=1,
        timestamp_ms=1720012345678,
        server_received_at_ms=int(time.time() * 1000),
        sampling_rate_hz=50,
        hand_ax=0.12,
        hand_ay=-0.04,
        hand_az=9.71,
        hand_gx=2.30,
        hand_gy=1.10,
        hand_gz=-0.40,
        shoe_ax=1.24,
        shoe_ay=0.33,
        shoe_az=9.22,
        shoe_gx=12.40,
        shoe_gy=4.20,
        shoe_gz=2.10,
    )
    test_db_session.add(record)
    test_db_session.commit()

    retrieved = test_db_session.query(SensorRecord).first()
    assert retrieved is not None
    assert retrieved.patient_id == "P001"
    assert retrieved.sequence == 1
    assert retrieved.hand_ax == 0.12
    assert retrieved.server_received_at_ms is not None


def test_fog_event_creation(test_db_session):
    """Test FOG event creation."""
    event = FOGEvent(
        event_id="test-event-001",
        patient_id="P001",
        detected_at_ms=1720012345678,
        confidence=0.91,
        cue_triggered=1,
        model_version="v1.0",
    )
    test_db_session.add(event)
    test_db_session.commit()

    retrieved = test_db_session.query(FOGEvent).filter_by(event_id="test-event-001").first()
    assert retrieved is not None
    assert retrieved.confidence == 0.91
    assert retrieved.cue_triggered == 1


def test_tremor_result_creation(test_db_session):
    """Test tremor result creation."""
    result = TremorResult(
        event_id="test-result-001",
        patient_id="P001",
        detected_at_ms=1720012345678,
        predicted_class="not_available",
        confidence=None,
        model_version="v1.0",
    )
    test_db_session.add(result)
    test_db_session.commit()

    retrieved = test_db_session.query(TremorResult).filter_by(event_id="test-result-001").first()
    assert retrieved is not None
    assert retrieved.predicted_class == "not_available"
    assert retrieved.confidence is None


def test_sensor_record_count(test_db_session):
    """Test sensor record counting."""
    # Add multiple records
    for i in range(5):
        record = SensorRecord(
            patient_id="P001",
            device_id="ESP32_001",
            sequence=i,
            timestamp_ms=1720012345678 + i * 1000,
            server_received_at_ms=int(time.time() * 1000),
            sampling_rate_hz=50,
            hand_ax=0.0, hand_ay=0.0, hand_az=9.8,
            hand_gx=0.0, hand_gy=0.0, hand_gz=0.0,
            shoe_ax=0.0, shoe_ay=0.0, shoe_az=9.8,
            shoe_gx=0.0, shoe_gy=0.0, shoe_gz=0.0,
        )
        test_db_session.add(record)
    test_db_session.commit()

    count = get_record_count(test_db_session)
    assert count == 5


def test_sensor_record_count_by_patient(test_db_session):
    """Test sensor record counting by patient."""
    # Add records for different patients
    for patient_id in ["P001", "P001", "P002"]:
        record = SensorRecord(
            patient_id=patient_id,
            device_id="ESP32_001",
            sequence=0,
            timestamp_ms=1720012345678,
            server_received_at_ms=int(time.time() * 1000),
            sampling_rate_hz=50,
            hand_ax=0.0, hand_ay=0.0, hand_az=9.8,
            hand_gx=0.0, hand_gy=0.0, hand_gz=0.0,
            shoe_ax=0.0, shoe_ay=0.0, shoe_az=9.8,
            shoe_gx=0.0, shoe_gy=0.0, shoe_gz=0.0,
        )
        test_db_session.add(record)
    test_db_session.commit()

    count_p001 = get_record_count(test_db_session, patient_id="P001")
    count_p002 = get_record_count(test_db_session, patient_id="P002")
    assert count_p001 == 2
    assert count_p002 == 1
