"""
Command schemas for PC to ESP32 communication.

This module defines the Pydantic models for commands sent from the
PC backend to ESP32 devices. Commands control device behavior,
including FOG cueing buzzer activation.

Protocol Version: 1.0

Fail-safe requirement:
FOG_CUE_ON commands include an optional duration_ms field.
Stage 2 ESP32 firmware MUST stop the buzzer locally after this
timeout even if FOG_CUE_OFF is never received. This prevents
indefinite cueing if the OFF command is lost due to disconnection
or PC crash.
"""

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CommandType(str, Enum):
    """
    Available command types for ESP32 control.

    Attributes:
        FOG_CUE_ON: Activate rhythmic buzzer cueing for FOG
        FOG_CUE_OFF: Deactivate buzzer cueing
        PING: Heartbeat ping to check device connectivity
        REQUEST_STATUS: Request device status information
    """
    FOG_CUE_ON = "FOG_CUE_ON"
    FOG_CUE_OFF = "FOG_CUE_OFF"
    PING = "PING"
    REQUEST_STATUS = "REQUEST_STATUS"


# Bounded cue duration limits (prototype safety)
MIN_CUE_DURATION_MS = 1000       # 1 second minimum
MAX_CUE_DURATION_MS = 30000      # 30 seconds maximum
DEFAULT_CUE_DURATION_MS = 10000  # 10 seconds default


class CommandPacket(BaseModel):
    """
    Command packet sent from PC backend to ESP32 device.

    This model defines the structure for controlling ESP32 behavior,
    including buzzer cueing for FOG events.

    For FOG_CUE_ON commands, the optional duration_ms field specifies
    the maximum cueing duration. Stage 2 ESP32 firmware MUST enforce
    this timeout locally as a safety mechanism.

    Protocol Version: 1.0
    """

    model_config = ConfigDict(
        use_enum=True,
        json_schema_extra={
            "examples": [{
                "protocol_version": "1.0",
                "message_type": "command",
                "command": "FOG_CUE_ON",
                "command_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp_ms": 1720012345678,
                "duration_ms": 10000,
            }]
        }
    )

    protocol_version: str = Field(
        default="1.0",
        description="Protocol version for backward compatibility",
        examples=["1.0"],
    )
    message_type: str = Field(
        default="command",
        description="Message type identifier",
        examples=["command"],
    )
    command: CommandType = Field(
        ...,
        description="Command to execute on ESP32",
        examples=["FOG_CUE_ON"],
    )
    command_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique command identifier for tracking",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    timestamp_ms: int = Field(
        ...,
        gt=0,
        description="Unix epoch timestamp in milliseconds",
        examples=[1720012345678],
    )
    duration_ms: Optional[int] = Field(
        default=None,
        description=(
            "Maximum cue duration in milliseconds (FOG_CUE_ON only). "
            "ESP32 MUST stop buzzer after this timeout even if FOG_CUE_OFF "
            "is not received. Valid range: 1000-30000 ms."
        ),
        examples=[10000],
        ge=MIN_CUE_DURATION_MS,
        le=MAX_CUE_DURATION_MS,
    )

    @field_validator('protocol_version')
    @classmethod
    def validate_protocol_version(cls, v: str) -> str:
        """Validate protocol version format."""
        if not v or not v.strip():
            raise ValueError('Protocol version cannot be empty')
        return v.strip()

    @field_validator('command_id')
    @classmethod
    def validate_command_id(cls, v: str) -> str:
        """Validate command ID format."""
        if not v or not v.strip():
            raise ValueError('Command ID cannot be empty')
        return v.strip()


def create_fog_cue_on_command(
    timestamp_ms: int,
    duration_ms: int = DEFAULT_CUE_DURATION_MS,
) -> CommandPacket:
    """
    Create a FOG_CUE_ON command packet.

    Args:
        timestamp_ms: Current Unix epoch timestamp in milliseconds
        duration_ms: Maximum cue duration in milliseconds

    Returns:
        CommandPacket: Configured command packet
    """
    return CommandPacket(
        command=CommandType.FOG_CUE_ON,
        timestamp_ms=timestamp_ms,
        duration_ms=duration_ms,
    )


def create_fog_cue_off_command(timestamp_ms: int) -> CommandPacket:
    """
    Create a FOG_CUE_OFF command packet.

    Args:
        timestamp_ms: Current Unix epoch timestamp in milliseconds

    Returns:
        CommandPacket: Configured command packet
    """
    return CommandPacket(
        command=CommandType.FOG_CUE_OFF,
        timestamp_ms=timestamp_ms,
    )


def create_ping_command(timestamp_ms: int) -> CommandPacket:
    """
    Create a PING command packet.

    Args:
        timestamp_ms: Current Unix epoch timestamp in milliseconds

    Returns:
        CommandPacket: Configured command packet
    """
    return CommandPacket(
        command=CommandType.PING,
        timestamp_ms=timestamp_ms,
    )


def create_request_status_command(timestamp_ms: int) -> CommandPacket:
    """
    Create a REQUEST_STATUS command packet.

    Args:
        timestamp_ms: Current Unix epoch timestamp in milliseconds

    Returns:
        CommandPacket: Configured command packet
    """
    return CommandPacket(
        command=CommandType.REQUEST_STATUS,
        timestamp_ms=timestamp_ms,
    )
