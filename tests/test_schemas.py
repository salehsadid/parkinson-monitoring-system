"""
Tests for Pydantic schemas.

This module tests the validation and serialization of sensor packets,
command packets, and event schemas.

Stage 1.1: Added tests for duration_ms validation and ConfigDict.
"""

import pytest
from pydantic import ValidationError

from pc_backend.app.schemas.sensor import IMUData, SensorPacket
from pc_backend.app.schemas.commands import (
    CommandPacket,
    CommandType,
    create_fog_cue_on_command,
    create_fog_cue_off_command,
    MIN_CUE_DURATION_MS,
    MAX_CUE_DURATION_MS,
    DEFAULT_CUE_DURATION_MS,
)
from pc_backend.app.schemas.events import FOGEvent, TremorResult, EventType, TremorClass


class TestIMUData:
    """Tests for IMUData schema."""

    def test_valid_imu_data(self):
        """Test valid IMU data creation."""
        data = IMUData(
            ax=0.12, ay=-0.04, az=9.71,
            gx=2.30, gy=1.10, gz=-0.40
        )
        assert data.ax == 0.12
        assert data.ay == -0.04
        assert data.az == 9.71
        assert data.gx == 2.30
        assert data.gy == 1.10
        assert data.gz == -0.40

    def test_imu_data_json_serialization(self):
        """Test IMU data JSON serialization."""
        data = IMUData(
            ax=0.12, ay=-0.04, az=9.71,
            gx=2.30, gy=1.10, gz=-0.40
        )
        json_data = data.model_dump()
        assert json_data["ax"] == 0.12
        assert json_data["ay"] == -0.04


class TestSensorPacket:
    """Tests for SensorPacket schema."""

    def test_valid_sensor_packet(self, sample_sensor_packet):
        """Test valid sensor packet creation."""
        packet = SensorPacket(**sample_sensor_packet)
        assert packet.patient_id == "P001"
        assert packet.device_id == "ESP32_001"
        assert packet.sequence == 12345
        assert packet.sampling_rate_hz == 50
        assert packet.hand.ax == 0.12
        assert packet.shoe.ax == 1.24

    def test_sensor_packet_missing_required_field(self):
        """Test sensor packet rejects missing required fields."""
        invalid_packet = {
            "protocol_version": "1.0",
            "message_type": "sensor_data",
            # Missing patient_id
            "device_id": "ESP32_001",
            "sequence": 1,
            "timestamp_ms": 1000,
            "sampling_rate_hz": 50,
            "hand": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
            "shoe": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
        }
        with pytest.raises(ValidationError):
            SensorPacket(**invalid_packet)

    def test_sensor_packet_invalid_sequence(self):
        """Test sensor packet rejects negative sequence."""
        invalid_packet = {
            "protocol_version": "1.0",
            "message_type": "sensor_data",
            "patient_id": "P001",
            "device_id": "ESP32_001",
            "sequence": -1,  # Invalid: negative
            "timestamp_ms": 1000,
            "sampling_rate_hz": 50,
            "hand": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
            "shoe": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
        }
        with pytest.raises(ValidationError):
            SensorPacket(**invalid_packet)

    def test_sensor_packet_invalid_sampling_rate(self):
        """Test sensor packet rejects zero sampling rate."""
        invalid_packet = {
            "protocol_version": "1.0",
            "message_type": "sensor_data",
            "patient_id": "P001",
            "device_id": "ESP32_001",
            "sequence": 1,
            "timestamp_ms": 1000,
            "sampling_rate_hz": 0,  # Invalid: must be > 0
            "hand": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
            "shoe": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
        }
        with pytest.raises(ValidationError):
            SensorPacket(**invalid_packet)

    def test_sensor_packet_empty_patient_id(self):
        """Test sensor packet rejects empty patient_id."""
        invalid_packet = {
            "protocol_version": "1.0",
            "message_type": "sensor_data",
            "patient_id": "",  # Invalid: empty
            "device_id": "ESP32_001",
            "sequence": 1,
            "timestamp_ms": 1000,
            "sampling_rate_hz": 50,
            "hand": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
            "shoe": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
        }
        with pytest.raises(ValidationError):
            SensorPacket(**invalid_packet)

    def test_sensor_packet_json_serialization(self, sample_sensor_packet):
        """Test sensor packet JSON serialization."""
        packet = SensorPacket(**sample_sensor_packet)
        json_data = packet.model_dump()
        assert json_data["patient_id"] == "P001"
        assert json_data["hand"]["ax"] == 0.12

    def test_sensor_packet_whitespace_patient_id(self):
        """Test sensor packet strips whitespace from patient_id."""
        packet_data = {
            "protocol_version": "1.0",
            "message_type": "sensor_data",
            "patient_id": "  P001  ",
            "device_id": "ESP32_001",
            "sequence": 1,
            "timestamp_ms": 1000,
            "sampling_rate_hz": 50,
            "hand": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
            "shoe": {"ax": 0, "ay": 0, "az": 9.8, "gx": 0, "gy": 0, "gz": 0},
        }
        packet = SensorPacket(**packet_data)
        assert packet.patient_id == "P001"


class TestCommandPacket:
    """Tests for CommandPacket schema."""

    def test_valid_command_packet(self, sample_command_packet):
        """Test valid command packet creation."""
        packet = CommandPacket(**sample_command_packet)
        assert packet.command == CommandType.FOG_CUE_ON
        assert packet.command_id == "550e8400-e29b-41d4-a716-446655440000"
        assert packet.timestamp_ms == 1720012345678

    def test_command_types(self):
        """Test all command types are valid."""
        for cmd_type in CommandType:
            packet = CommandPacket(
                command=cmd_type,
                timestamp_ms=1000,
            )
            assert packet.command == cmd_type

    def test_command_packet_json_serialization(self, sample_command_packet):
        """Test command packet JSON serialization."""
        packet = CommandPacket(**sample_command_packet)
        json_data = packet.model_dump()
        assert json_data["command"] == "FOG_CUE_ON"

    def test_command_packet_duration_ms_valid(self):
        """Test command packet with valid duration_ms."""
        packet = CommandPacket(
            command=CommandType.FOG_CUE_ON,
            timestamp_ms=1000,
            duration_ms=10000,
        )
        assert packet.duration_ms == 10000

    def test_command_packet_duration_ms_min_boundary(self):
        """Test command packet with minimum duration_ms."""
        packet = CommandPacket(
            command=CommandType.FOG_CUE_ON,
            timestamp_ms=1000,
            duration_ms=MIN_CUE_DURATION_MS,
        )
        assert packet.duration_ms == MIN_CUE_DURATION_MS

    def test_command_packet_duration_ms_max_boundary(self):
        """Test command packet with maximum duration_ms."""
        packet = CommandPacket(
            command=CommandType.FOG_CUE_ON,
            timestamp_ms=1000,
            duration_ms=MAX_CUE_DURATION_MS,
        )
        assert packet.duration_ms == MAX_CUE_DURATION_MS

    def test_command_packet_duration_ms_below_min(self):
        """Test command packet rejects duration_ms below minimum."""
        with pytest.raises(ValidationError):
            CommandPacket(
                command=CommandType.FOG_CUE_ON,
                timestamp_ms=1000,
                duration_ms=MIN_CUE_DURATION_MS - 1,
            )

    def test_command_packet_duration_ms_above_max(self):
        """Test command packet rejects duration_ms above maximum."""
        with pytest.raises(ValidationError):
            CommandPacket(
                command=CommandType.FOG_CUE_ON,
                timestamp_ms=1000,
                duration_ms=MAX_CUE_DURATION_MS + 1,
            )

    def test_command_packet_duration_ms_none(self):
        """Test command packet allows None duration_ms."""
        packet = CommandPacket(
            command=CommandType.FOG_CUE_ON,
            timestamp_ms=1000,
            duration_ms=None,
        )
        assert packet.duration_ms is None

    def test_create_fog_cue_on_command_default_duration(self):
        """Test create_fog_cue_on_command uses default duration."""
        command = create_fog_cue_on_command(timestamp_ms=1000)
        assert command.command == CommandType.FOG_CUE_ON
        assert command.duration_ms == DEFAULT_CUE_DURATION_MS

    def test_create_fog_cue_on_command_custom_duration(self):
        """Test create_fog_cue_on_command with custom duration."""
        command = create_fog_cue_on_command(timestamp_ms=1000, duration_ms=5000)
        assert command.duration_ms == 5000

    def test_create_fog_cue_off_command_no_duration(self):
        """Test create_fog_cue_off_command has no duration."""
        command = create_fog_cue_off_command(timestamp_ms=1000)
        assert command.command == CommandType.FOG_CUE_OFF
        assert command.duration_ms is None


class TestFOGEvent:
    """Tests for FOGEvent schema."""

    def test_valid_fog_event(self, sample_fog_event):
        """Test valid FOG event creation."""
        event = FOGEvent(**sample_fog_event)
        assert event.patient_id == "P001"
        assert event.event_type == EventType.FOG
        assert event.confidence == 0.91
        assert event.cue_triggered is True

    def test_fog_event_invalid_confidence(self):
        """Test FOG event rejects invalid confidence."""
        invalid_event = {
            "event_id": "test",
            "patient_id": "P001",
            "event_type": "FOG",
            "detected_at_ms": 1000,
            "confidence": 1.5,  # Invalid: > 1.0
            "cue_triggered": False,
            "model_version": "v1.0",
        }
        with pytest.raises(ValidationError):
            FOGEvent(**invalid_event)


class TestTremorResult:
    """Tests for TremorResult schema."""

    def test_valid_tremor_result(self, sample_tremor_result):
        """Test valid tremor result creation."""
        result = TremorResult(**sample_tremor_result)
        assert result.patient_id == "P001"
        assert result.event_type == EventType.TREMOR_RESULT
        assert result.predicted_class == TremorClass.NOT_AVAILABLE
        assert result.confidence is None

    def test_tremor_result_with_confidence(self):
        """Test tremor result with confidence score."""
        result_data = {
            "event_id": "test",
            "patient_id": "P001",
            "event_type": "TREMOR_RESULT",
            "detected_at_ms": 1000,
            "predicted_class": "mild",
            "confidence": 0.85,
            "model_version": "v1.0",
        }
        result = TremorResult(**result_data)
        assert result.predicted_class == "mild"
        assert result.confidence == 0.85
