"""
WebSocket connection manager for ESP32 device connectivity.

This module manages WebSocket connections from ESP32 devices and
simulators. It provides methods to connect, disconnect, and send
commands to specific devices.

Stage 1 Implementation:
- In-memory connection storage
- Single worker assumption
- No authentication (for simplicity)
- Basic connection tracking

Future Enhancements:
- Redis for multi-worker support
- Authentication and authorization
- Connection pooling
- Heartbeat monitoring
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager for ESP32 devices.

    Manages active WebSocket connections and provides methods
    to send commands to specific devices.
    """

    def __init__(self):
        """Initialize connection manager."""
        self._connections: Dict[str, WebSocket] = {}
        self._device_info: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, device_id: str) -> None:
        """
        Accept and register a new device connection.

        Args:
            websocket: WebSocket connection object
            device_id: Unique device identifier
        """
        await websocket.accept()
        self._connections[device_id] = websocket
        self._device_info[device_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "last_message_at": None,
            "message_count": 0,
        }
        logger.info(f"Device connected: {device_id}")

    def disconnect(self, device_id: str) -> None:
        """
        Remove a device connection.

        Args:
            device_id: Unique device identifier
        """
        if device_id in self._connections:
            del self._connections[device_id]
        if device_id in self._device_info:
            del self._device_info[device_id]
        logger.info(f"Device disconnected: {device_id}")

    def is_connected(self, device_id: str) -> bool:
        """
        Check if a device is currently connected.

        Args:
            device_id: Unique device identifier

        Returns:
            bool: True if device is connected
        """
        return device_id in self._connections

    def get_connection(self, device_id: str) -> Optional[WebSocket]:
        """
        Get WebSocket connection for a device.

        Args:
            device_id: Unique device identifier

        Returns:
            Optional[WebSocket]: WebSocket connection or None
        """
        return self._connections.get(device_id)

    def get_device_info(self, device_id: str) -> Optional[dict]:
        """
        Get connection info for a device.

        Args:
            device_id: Unique device identifier

        Returns:
            Optional[dict]: Device connection info or None
        """
        return self._device_info.get(device_id)

    def list_connected_devices(self) -> List[str]:
        """
        List all currently connected device IDs.

        Returns:
            List[str]: List of connected device IDs
        """
        return list(self._connections.keys())

    def get_connection_count(self) -> int:
        """
        Get the number of active connections.

        Returns:
            int: Number of connected devices
        """
        return len(self._connections)

    async def send_json(self, device_id: str, data: dict) -> bool:
        """
        Send JSON data to a specific device.

        Args:
            device_id: Target device identifier
            data: Dictionary to send as JSON

        Returns:
            bool: True if sent successfully, False otherwise
        """
        websocket = self._connections.get(device_id)
        if websocket is None:
            logger.warning(f"Cannot send to disconnected device: {device_id}")
            return False

        try:
            await websocket.send_text(json.dumps(data))
            self._device_info[device_id]["last_message_at"] = datetime.utcnow().isoformat()
            self._device_info[device_id]["message_count"] += 1
            return True
        except Exception as e:
            logger.error(f"Error sending to device {device_id}: {e}")
            return False

    async def send_command(self, device_id: str, command: dict) -> bool:
        """
        Send a command to a specific device.

        Args:
            device_id: Target device identifier
            command: Command dictionary to send

        Returns:
            bool: True if sent successfully, False otherwise
        """
        return await self.send_json(device_id, command)

    async def broadcast(self, data: dict, exclude: Optional[str] = None) -> int:
        """
        Broadcast JSON data to all connected devices.

        Args:
            data: Dictionary to broadcast
            exclude: Optional device ID to exclude

        Returns:
            int: Number of devices successfully sent to
        """
        sent_count = 0
        for device_id, websocket in self._connections.items():
            if device_id == exclude:
                continue
            try:
                await websocket.send_text(json.dumps(data))
                sent_count += 1
            except Exception as e:
                logger.error(f"Error broadcasting to {device_id}: {e}")

        return sent_count

    def update_last_message(self, device_id: str) -> None:
        """
        Update the last message timestamp for a device.

        Args:
            device_id: Device identifier
        """
        if device_id in self._device_info:
            self._device_info[device_id]["last_message_at"] = datetime.utcnow().isoformat()
            self._device_info[device_id]["message_count"] += 1


# Global connection manager instance
connection_manager = ConnectionManager()
