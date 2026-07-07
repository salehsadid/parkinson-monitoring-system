"""
Database base model and initialization for SQLAlchemy.

This module provides the base model class and database initialization
utilities for the Parkinson's Monitoring System.

Database: SQLite (local file-based database)
Tables: Patient, Device, SensorRecord, FOGEvent, TremorResult
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    event,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from pc_backend.app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Patient(Base):
    """
    Patient information table.

    Stores basic patient metadata. In Stage 1, this is minimal.
    Future stages may add demographics, clinical notes, etc.
    """

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, patient_id='{self.patient_id}')>"


class Device(Base):
    """
    Device information table.

    Tracks ESP32 devices and their association with patients.
    A device is permanently associated with its first registered patient.
    """

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), unique=True, nullable=False, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Device(id={self.id}, device_id='{self.device_id}', patient_id='{self.patient_id}')>"


class SensorRecord(Base):
    """
    Sensor data records table.

    Stores raw IMU readings from both hand and shoe sensors.
    This is the primary data table for sensor streams.

    Units:
    - Acceleration (ax, ay, az): m/s²
    - Gyroscope (gx, gy, gz): degrees/second

    Timestamps:
    - timestamp_ms: Device-provided timestamp (may be inaccurate)
    - server_received_at_ms: Backend receive timestamp (reliable)
    """

    __tablename__ = "sensor_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    device_id = Column(String(50), ForeignKey("devices.device_id"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    timestamp_ms = Column(Integer, nullable=False, index=True)
    server_received_at_ms = Column(Integer, nullable=False, index=True)
    sampling_rate_hz = Column(Integer, nullable=False)

    # Hand sensor (tremor analysis)
    hand_ax = Column(Float, nullable=False)
    hand_ay = Column(Float, nullable=False)
    hand_az = Column(Float, nullable=False)
    hand_gx = Column(Float, nullable=False)
    hand_gy = Column(Float, nullable=False)
    hand_gz = Column(Float, nullable=False)

    # Shoe sensor (FOG detection)
    shoe_ax = Column(Float, nullable=False)
    shoe_ay = Column(Float, nullable=False)
    shoe_az = Column(Float, nullable=False)
    shoe_gx = Column(Float, nullable=False)
    shoe_gy = Column(Float, nullable=False)
    shoe_gz = Column(Float, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<SensorRecord(id={self.id}, patient_id='{self.patient_id}', "
            f"sequence={self.sequence})>"
        )


class FOGEvent(Base):
    """
    Freezing of Gait detection events table.

    Stores detected FOG events from the ML inference pipeline.
    """

    __tablename__ = "fog_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    detected_at_ms = Column(Integer, nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    cue_triggered = Column(Integer, nullable=False, default=0)  # 0=False, 1=True
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<FOGEvent(id={self.id}, event_id='{self.event_id}', "
            f"confidence={self.confidence})>"
        )


class TremorResult(Base):
    """
    Tremor analysis results table.

    Stores tremor analysis output from the ML inference pipeline.
    """

    __tablename__ = "tremor_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    patient_id = Column(String(50), ForeignKey("patients.patient_id"), nullable=False, index=True)
    detected_at_ms = Column(Integer, nullable=False, index=True)
    predicted_class = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=True)  # Can be None
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<TremorResult(id={self.id}, event_id='{self.event_id}', "
            f"predicted_class='{self.predicted_class}')>"
        )


def _configure_sqlite_engine(engine) -> None:
    """
    Apply SQLite-specific PRAGMA settings to an engine.

    Only applies to SQLite databases. No-ops for other database types.

    Args:
        engine: SQLAlchemy engine to configure
    """
    url = str(engine.url)
    if not url.startswith("sqlite"):
        return

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_configured_engine(database_url: Optional[str] = None):
    """
    Create a SQLAlchemy engine with proper configuration.

    For SQLite databases, applies WAL journal mode and foreign_keys PRAGMAs.

    Args:
        database_url: Optional database URL override

    Returns:
        Engine: Configured SQLAlchemy engine
    """
    url = database_url or settings.DATABASE_URL
    engine = create_engine(url, echo=False, connect_args={"check_same_thread": False} if "sqlite" in url else {})
    _configure_sqlite_engine(engine)
    return engine


def init_database(database_url: Optional[str] = None) -> None:
    """
    Initialize the database and create all tables.

    Uses a dedicated engine for initialization that is disposed after use.
    Runtime sessions should use DatabaseManager.

    Args:
        database_url: Optional database URL override
    """
    engine = create_configured_engine(database_url)
    Base.metadata.create_all(engine)
    engine.dispose()


def get_session_factory(database_url: Optional[str] = None):
    """
    Get a session factory for database operations.

    Args:
        database_url: Optional database URL override

    Returns:
        sessionmaker: Configured session factory
    """
    engine = create_configured_engine(database_url)
    return sessionmaker(bind=engine)
