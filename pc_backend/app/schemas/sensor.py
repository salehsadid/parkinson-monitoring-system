"""
Sensor data schemas for IMU readings from MPU6050 sensors.

This module defines the Pydantic models for validating and serializing
sensor data packets from ESP32 devices with dual MPU6050 sensors.

Units:
- Acceleration (ax, ay, az): m/s²
- Gyroscope (gx, gy, gz): degrees/second
- Timestamp: Unix epoch milliseconds

Coordinate Frame Notes:
- Hand sensor: Mounted on glove/ring, orientation depends on mounting
- Shoe sensor: Mounted on shoe, orientation depends on mounting
- Future preprocessing may require calibration, axis normalization,
  and orientation handling based on actual mounting positions
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class IMUData(BaseModel):
    """
    Single MPU6050 IMU reading containing acceleration and gyroscope data.

    This model represents data from one MPU6050 sensor unit.
    The coordinate system follows the sensor's native frame.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "ax": 0.12,
                "ay": -0.04,
                "az": 9.71,
                "gx": 2.30,
                "gy": 1.10,
                "gz": -0.40,
            }]
        }
    )

    ax: float = Field(
        ...,
        description="Acceleration X-axis (m/s²)",
        examples=[0.12],
    )
    ay: float = Field(
        ...,
        description="Acceleration Y-axis (m/s²)",
        examples=[-0.04],
    )
    az: float = Field(
        ...,
        description="Acceleration Z-axis (m/s²)",
        examples=[9.71],
    )
    gx: float = Field(
        ...,
        description="Gyroscope X-axis (degrees/second)",
        examples=[2.30],
    )
    gy: float = Field(
        ...,
        description="Gyroscope Y-axis (degrees/second)",
        examples=[1.10],
    )
    gz: float = Field(
        ...,
        description="Gyroscope Z-axis (degrees/second)",
        examples=[-0.40],
    )


class SensorPacket(BaseModel):
    """
    Complete sensor data packet from ESP32 with dual MPU6050 sensors.

    This is the primary data contract between ESP32 and PC backend.
    Each packet contains synchronized readings from both hand (tremor)
    and shoe (FOG) sensors.

    Protocol Version: 1.0
    """

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
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
            }]
        }
    )

    protocol_version: str = Field(
        default="1.0",
        description="Protocol version for backward compatibility",
        examples=["1.0"],
    )
    message_type: str = Field(
        default="sensor_data",
        description="Message type identifier",
        examples=["sensor_data"],
    )
    patient_id: str = Field(
        ...,
        min_length=1,
        description="Unique patient identifier",
        examples=["P001"],
    )
    device_id: str = Field(
        ...,
        min_length=1,
        description="ESP32 device identifier",
        examples=["ESP32_001"],
    )
    sequence: int = Field(
        ...,
        ge=0,
        description="Monotonically increasing sequence number",
        examples=[12345],
    )
    timestamp_ms: int = Field(
        ...,
        gt=0,
        description="Unix epoch timestamp in milliseconds (device-provided)",
        examples=[1720012345678],
    )
    sampling_rate_hz: int = Field(
        ...,
        gt=0,
        description="Actual sampling rate in Hz",
        examples=[50],
    )
    hand: IMUData = Field(
        ...,
        description="Hand sensor (tremor analysis) IMU data",
    )
    shoe: IMUData = Field(
        ...,
        description="Shoe sensor (FOG detection) IMU data",
    )

    @field_validator('protocol_version')
    @classmethod
    def validate_protocol_version(cls, v: str) -> str:
        """Validate protocol version format."""
        if not v or not v.strip():
            raise ValueError('Protocol version cannot be empty')
        return v.strip()

    @field_validator('patient_id')
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        """Validate patient ID format."""
        if not v or not v.strip():
            raise ValueError('Patient ID cannot be empty')
        return v.strip()

    @field_validator('device_id')
    @classmethod
    def validate_device_id(cls, v: str) -> str:
        """Validate device ID format."""
        if not v or not v.strip():
            raise ValueError('Device ID cannot be empty')
        return v.strip()
