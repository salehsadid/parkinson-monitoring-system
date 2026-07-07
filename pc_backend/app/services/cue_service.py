"""
Cue service for FOG (Freezing of Gait) buzzer activation.

This module provides the CueService class responsible for managing
FOG cue commands. When FOG is detected by the ML model, this service
sends commands to ESP32 devices to activate/deactivate the buzzer.

Cue Flow:
1. ML model detects FOG event
2. CueService creates FOG_CUE_ON command with duration_ms
3. Command is sent to connected ESP32 via WebSocket
4. ESP32 activates buzzer with rhythmic pattern
5. ESP32 MUST stop buzzer after duration_ms even if FOG_CUE_OFF not received
6. After detection ends, FOG_CUE_OFF command is sent
7. ESP32 deactivates buzzer

Stage 1.1 Safety Requirement:
- FOG_CUE_ON commands include duration_ms field
- ESP32 firmware (Stage 2) MUST enforce this timeout locally
- This prevents indefinite cueing if OFF command is lost

Future Enhancements:
- Adaptive cue duration based on patient response
- Cue intensity configuration
- Multiple cue patterns
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Optional

from pc_backend.app.core.config import settings
from pc_backend.app.schemas.commands import (
    CommandPacket,
    CommandType,
    create_fog_cue_on_command,
    create_fog_cue_off_command,
    DEFAULT_CUE_DURATION_MS,
)
from pc_backend.app.websocket.manager import connection_manager

logger = logging.getLogger(__name__)


class CueService:
    """
    Service for managing FOG cue commands.

    This service handles the creation and sending of buzzer
    cue commands to ESP32 devices when FOG is detected.
    """

    def __init__(self):
        """Initialize cue service."""
        self._active_cues: dict = {}  # device_id -> cue_info

    async def trigger_fog_cue(
        self,
        device_id: str,
        patient_id: str,
        confidence: float,
        model_version: str = "not_trained",
        duration_ms: Optional[int] = None,
    ) -> Optional[str]:
        """
        Trigger FOG buzzer cueing on a device.

        This method sends a FOG_CUE_ON command to the specified device.
        The device should activate its buzzer with a rhythmic pattern.

        Safety: The command includes duration_ms. ESP32 firmware MUST
        stop the buzzer after this timeout even if FOG_CUE_OFF is
        never received. This prevents indefinite cueing.

        Args:
            device_id: Target ESP32 device identifier
            patient_id: Patient identifier for logging
            confidence: FOG detection confidence score
            model_version: ML model version used for detection
            duration_ms: Maximum cue duration (ms), None uses default

        Returns:
            Optional[str]: Command ID if sent successfully, None otherwise
        """
        # Check if device is connected
        if not connection_manager.is_connected(device_id):
            logger.warning(f"Cannot trigger cue: Device {device_id} not connected")
            return None

        # Create command with duration
        timestamp_ms = int(time.time() * 1000)
        cue_duration = duration_ms or DEFAULT_CUE_DURATION_MS
        command = create_fog_cue_on_command(timestamp_ms, duration_ms=cue_duration)

        # Send command
        success = await connection_manager.send_command(
            device_id,
            command.model_dump(),
        )

        if success:
            # Track active cue
            self._active_cues[device_id] = {
                "command_id": command.command_id,
                "patient_id": patient_id,
                "confidence": confidence,
                "model_version": model_version,
                "duration_ms": cue_duration,
                "started_at": datetime.utcnow().isoformat(),
            }
            logger.info(
                f"FOG cue triggered on {device_id} for patient {patient_id} "
                f"(confidence: {confidence:.2f}, duration: {cue_duration}ms, "
                f"command_id: {command.command_id})"
            )
            return command.command_id
        else:
            logger.error(f"Failed to send FOG cue command to {device_id}")
            return None

    async def stop_fog_cue(self, device_id: str) -> Optional[str]:
        """
        Stop FOG buzzer cueing on a device.

        This method sends a FOG_CUE_OFF command to the specified device.
        The device should deactivate its buzzer.

        Args:
            device_id: Target ESP32 device identifier

        Returns:
            Optional[str]: Command ID if sent successfully, None otherwise
        """
        # Check if device is connected
        if not connection_manager.is_connected(device_id):
            logger.warning(f"Cannot stop cue: Device {device_id} not connected")
            return None

        # Create command
        timestamp_ms = int(time.time() * 1000)
        command = create_fog_cue_off_command(timestamp_ms)

        # Send command
        success = await connection_manager.send_command(
            device_id,
            command.model_dump(),
        )

        if success:
            # Remove from active cues
            if device_id in self._active_cues:
                del self._active_cues[device_id]
            logger.info(
                f"FOG cue stopped on {device_id} (command_id: {command.command_id})"
            )
            return command.command_id
        else:
            logger.error(f"Failed to send FOG cue off command to {device_id}")
            return None

    def get_active_cue(self, device_id: str) -> Optional[dict]:
        """
        Get information about an active cue on a device.

        Args:
            device_id: Device identifier

        Returns:
            Optional[dict]: Active cue information or None
        """
        return self._active_cues.get(device_id)

    def get_all_active_cues(self) -> dict:
        """
        Get information about all active cues.

        Returns:
            dict: Dictionary of device_id -> cue_info
        """
        return self._active_cues.copy()

    def is_cue_active(self, device_id: str) -> bool:
        """
        Check if a cue is currently active on a device.

        Args:
            device_id: Device identifier

        Returns:
            bool: True if cue is active
        """
        return device_id in self._active_cues

    async def send_ping(self, device_id: str) -> Optional[str]:
        """
        Send a ping command to check device connectivity.

        Args:
            device_id: Target device identifier

        Returns:
            Optional[str]: Command ID if sent successfully, None otherwise
        """
        if not connection_manager.is_connected(device_id):
            return None

        timestamp_ms = int(time.time() * 1000)
        command = CommandPacket(
            command=CommandType.PING,
            timestamp_ms=timestamp_ms,
        )

        success = await connection_manager.send_command(
            device_id,
            command.model_dump(),
        )

        return command.command_id if success else None


# Global cue service instance
cue_service = CueService()
