"""
Pytest configuration and fixtures for the Parkinson's Monitoring System.

This module provides test fixtures for database sessions, test clients,
and other test utilities.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pc_backend.app.database.base import Base
from pc_backend.app.database.session import get_db
from pc_backend.app.main import app


@pytest.fixture(scope="function")
def test_db_engine():
    """
    Create a test database engine with in-memory SQLite.

    Yields:
        Engine: SQLAlchemy engine for test database
    """
    engine = create_engine("sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """
    Create a test database session.

    Args:
        test_db_engine: Test database engine fixture

    Yields:
        Session: Database session for testing
    """
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_client(test_db_engine):
    """
    Create a FastAPI test client.

    Args:
        test_db_engine: Test database engine fixture

    Yields:
        TestClient: FastAPI test client
    """
    SessionLocal = sessionmaker(bind=test_db_engine)

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_sensor_packet():
    """
    Provide a sample valid sensor packet.

    Returns:
        dict: Valid sensor packet
    """
    return {
        "protocol_version": "1.0",
        "message_type": "sensor_data",
        "patient_id": "P001",
        "device_id": "ESP32_001",
        "sequence": 12345,
        "timestamp_ms": 1720012345678,
        "sampling_rate_hz": 50,
        "hand": {
            "ax": 0.12,
            "ay": -0.04,
            "az": 9.71,
            "gx": 2.30,
            "gy": 1.10,
            "gz": -0.40,
        },
        "shoe": {
            "ax": 1.24,
            "ay": 0.33,
            "az": 9.22,
            "gx": 12.40,
            "gy": 4.20,
            "gz": 2.10,
        },
    }


@pytest.fixture
def sample_command_packet():
    """
    Provide a sample valid command packet.

    Returns:
        dict: Valid command packet
    """
    return {
        "protocol_version": "1.0",
        "message_type": "command",
        "command": "FOG_CUE_ON",
        "command_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp_ms": 1720012345678,
    }


@pytest.fixture
def sample_fog_event():
    """
    Provide a sample valid FOG event.

    Returns:
        dict: Valid FOG event
    """
    return {
        "event_id": "550e8400-e29b-41d4-a716-446655440000",
        "patient_id": "P001",
        "event_type": "FOG",
        "detected_at_ms": 1720012345678,
        "confidence": 0.91,
        "cue_triggered": True,
        "model_version": "v1.0",
    }


@pytest.fixture
def sample_tremor_result():
    """
    Provide a sample valid tremor result.

    Returns:
        dict: Valid tremor result
    """
    return {
        "event_id": "550e8400-e29b-41d4-a716-446655440000",
        "patient_id": "P001",
        "event_type": "TREMOR_RESULT",
        "detected_at_ms": 1720012345678,
        "predicted_class": "not_available",
        "confidence": None,
        "model_version": "v1.0",
    }
