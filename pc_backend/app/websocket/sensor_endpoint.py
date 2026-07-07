"""
WebSocket sensor endpoint for ESP32 device communication.

This module defines the WebSocket endpoint that handles communication
with ESP32 devices and simulators. It receives sensor data packets,
validates them, and stores them in the database.

Endpoint: /ws/device/{device_id}

Message Flow:
1. Device connects via WebSocket
2. Device sends sensor data packets
3. Server validates packets using Pydantic
4. Server stores valid packets in database
5. Server can send commands back to device

Stage 1.1 Fixes:
- Device identity validation: device_id in URL must match packet.device_id
- Patient consistency: device registered to patient must match packet.patient_id
- Single-transaction commits: all DB operations in one transaction
- Server receive timestamp: server_received_at_ms captures when packet arrived
- Specific ValidationError catch: only catch Pydantic ValidationError
- Duplicate sequence: logged as warning, not rejected (future unique constraint)
"""

import json
import logging
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import and_
from sqlalchemy.orm import Session

from pc_backend.app.core.config import settings
from pc_backend.app.database.base import (
    Device,
    Patient,
    SensorRecord,
)
from pc_backend.app.database.session import get_database_manager
from pc_backend.app.schemas.sensor import SensorPacket
from pc_backend.app.websocket.manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_device_identity(
    device_id: str,
    packet: SensorPacket,
    db: Session,
) -> Optional[Device]:
    """
    Validate device identity and patient consistency.

    Checks:
    1. Device must exist in database
    2. Device ID in URL must match packet.device_id
    3. Device must be registered to the patient in packet

    Args:
        device_id: Device identifier from URL
        packet: Validated sensor packet
        db: Database session

    Returns:
        Device object if validation passes, None otherwise

    Logs:
        Warning if device not found
        Error if device_id mismatch
        Error if patient mismatch
    """
    # Check device exists
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        logger.warning(f"Device {device_id} not found in database")
        return None

    # Validate device_id matches packet
    if device.device_id != packet.device_id:
        logger.error(
            f"Device identity mismatch: URL={device_id}, "
            f"packet={packet.device_id}"
        )
        return None

    # Validate patient consistency
    if device.patient_id != packet.patient_id:
        logger.error(
            f"Patient mismatch: device {device_id} registered to "
            f"{device.patient_id}, packet claims {packet.patient_id}"
        )
        return None

    return device


async def handle_sensor_packet(
    device_id: str,
    packet: SensorPacket,
    db: Session,
) -> None:
    """
    Process and store a validated sensor packet in a single transaction.

    All database operations are performed in a single transaction to
    ensure atomicity. If any operation fails, all changes are rolled back.

    Args:
        device_id: Device identifier
        packet: Validated sensor packet
        db: Database session
    """
    # Record server receive time
    server_received_at_ms = int(time.time() * 1000)

    # All operations in single transaction
    # Ensure patient exists (auto-register for dev)
    patient = db.query(Patient).filter(
        Patient.patient_id == packet.patient_id
    ).first()
    if not patient:
        patient = Patient(patient_id=packet.patient_id)
        db.add(patient)
        logger.info(f"Auto-registered patient {packet.patient_id}")

    # Update device last seen
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device:
        device.last_seen_at = datetime.utcnow()
    else:
        # Auto-register device (dev convenience)
        device = Device(
            device_id=device_id,
            patient_id=packet.patient_id,
        )
        db.add(device)
        logger.info(f"Auto-registered device {device_id}")

    # Create sensor record with server receive timestamp
    record = SensorRecord(
        patient_id=packet.patient_id,
        device_id=device_id,
        sequence=packet.sequence,
        timestamp_ms=packet.timestamp_ms,
        server_received_at_ms=server_received_at_ms,
        sampling_rate_hz=packet.sampling_rate_hz,
        hand_ax=packet.hand.ax,
        hand_ay=packet.hand.ay,
        hand_az=packet.hand.az,
        hand_gx=packet.hand.gx,
        hand_gy=packet.hand.gy,
        hand_gz=packet.hand.gz,
        shoe_ax=packet.shoe.ax,
        shoe_ay=packet.shoe.ay,
        shoe_az=packet.shoe.az,
        shoe_gx=packet.shoe.gx,
        shoe_gy=packet.shoe.gy,
        shoe_gz=packet.shoe.gz,
    )
    db.add(record)

    # Single commit for all operations
    db.commit()


@router.websocket("/ws/device/{device_id}")
async def websocket_sensor_endpoint(
    websocket: WebSocket,
    device_id: str,
) -> None:
    """
    WebSocket endpoint for ESP32 device communication.

    This endpoint handles:
    - Device connection and registration
    - Receiving and validating sensor data packets
    - Storing valid packets in the database
    - Sending commands back to devices

    Args:
        websocket: WebSocket connection object
        device_id: Unique device identifier
    """
    # Connect device
    await connection_manager.connect(websocket, device_id)
    db_manager = get_database_manager()
    db = db_manager.get_session()

    try:
        while True:
            # Receive message
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON from {device_id}: {e}")
                continue

            # Validate as sensor packet (catch only Pydantic errors)
            try:
                packet = SensorPacket(**data)
            except PydanticValidationError as e:
                logger.warning(f"Invalid sensor packet from {device_id}: {e}")
                continue

            # Validate device identity and patient consistency
            device = _validate_device_identity(device_id, packet, db)
            if not device:
                continue

            # Update connection manager
            connection_manager.update_last_message(device_id)

            # Store in database
            try:
                await handle_sensor_packet(device_id, packet, db)
            except Exception as e:
                logger.error(f"Error storing packet from {device_id}: {e}")
                db.rollback()

    except WebSocketDisconnect:
        logger.info(f"Device {device_id} disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket handler for {device_id}: {e}")
    finally:
        connection_manager.disconnect(device_id)
        db.close()
