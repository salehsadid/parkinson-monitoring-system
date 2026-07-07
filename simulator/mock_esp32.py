"""
Mock ESP32 simulator for testing the Parkinson's Monitoring System.

This module simulates an ESP32 device with dual MPU6050 sensors,
connecting to the PC backend via WebSocket and sending synthetic
sensor data.

Usage:
    python mock_esp32.py --device-id ESP32_001 --patient-id P001

Features:
- Connects to FastAPI WebSocket endpoint
- Generates synthetic hand and shoe IMU data
- Sends packets at configurable rate
- Receives and prints commands from PC
- Supports different signal modes (baseline, tremor-like, gait-like)

Important Disclaimer:
This simulator generates synthetic data for SOFTWARE TESTING ONLY.
The signals do NOT represent medically valid Parkinsonian tremor
or clinically valid Freezing of Gait (FOG) patterns.
"""

import argparse
import asyncio
import json
import logging
import time
import uuid
from typing import Optional

import websockets

from signal_generator import SignalGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class MockESP32:
    """
    Mock ESP32 simulator with dual MPU6050 sensors.

    Simulates an ESP32 device that sends hand and shoe sensor data
    to the PC backend via WebSocket.
    """

    def __init__(
        self,
        device_id: str = "ESP32_001",
        patient_id: str = "P001",
        server_url: str = "ws://localhost:8000",
        sampling_rate_hz: int = 50,
        signal_mode: str = "baseline",
    ):
        """
        Initialize mock ESP32 simulator.

        Args:
            device_id: Unique device identifier
            patient_id: Patient identifier
            server_url: WebSocket server URL
            sampling_rate_hz: Sampling rate in Hz
            signal_mode: Signal generation mode
        """
        self.device_id = device_id
        self.patient_id = patient_id
        self.server_url = server_url
        self.sampling_rate_hz = sampling_rate_hz
        self.signal_mode = signal_mode

        self.signal_generator = SignalGenerator(sampling_rate_hz)
        self.sequence = 0
        self.running = False
        self.websocket = None

    def generate_packet(self) -> dict:
        """
        Generate a sensor data packet.

        Returns:
            dict: Sensor packet in the expected format
        """
        # Generate signals based on mode
        if self.signal_mode == "tremor_like":
            hand_data, shoe_data = self.signal_generator.generate_tremor_like()
        elif self.signal_mode == "gait_like":
            hand_data, shoe_data = self.signal_generator.generate_gait_like()
        elif self.signal_mode == "fog_like":
            hand_data, shoe_data = self.signal_generator.generate_fog_like()
        else:
            hand_data, shoe_data = self.signal_generator.generate_baseline()

        # Create packet
        packet = {
            "protocol_version": "1.0",
            "message_type": "sensor_data",
            "patient_id": self.patient_id,
            "device_id": self.device_id,
            "sequence": self.sequence,
            "timestamp_ms": int(time.time() * 1000),
            "sampling_rate_hz": self.sampling_rate_hz,
            "hand": {
                "ax": float(hand_data[0, 0]),
                "ay": float(hand_data[0, 1]),
                "az": float(hand_data[0, 2]),
                "gx": float(hand_data[0, 3]),
                "gy": float(hand_data[0, 4]),
                "gz": float(hand_data[0, 5]),
            },
            "shoe": {
                "ax": float(shoe_data[0, 0]),
                "ay": float(shoe_data[0, 1]),
                "az": float(shoe_data[0, 2]),
                "gx": float(shoe_data[0, 3]),
                "gy": float(shoe_data[0, 4]),
                "gz": float(shoe_data[0, 5]),
            },
        }

        self.sequence += 1
        return packet

    async def receive_commands(self) -> None:
        """Listen for commands from the server."""
        try:
            while self.running and self.websocket:
                message = await self.websocket.recv()
                try:
                    command = json.loads(message)
                    logger.info(f"Received command: {command.get('command', 'unknown')}")
                    logger.debug(f"Command details: {command}")
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {message}")
        except websockets.ConnectionClosed:
            logger.info("Connection closed while receiving commands")
        except Exception as e:
            logger.error(f"Error receiving commands: {e}")

    async def connect_and_send(self) -> None:
        """Connect to server and send sensor data."""
        uri = f"{self.server_url}/ws/device/{self.device_id}"

        while True:
            try:
                logger.info(f"Connecting to {uri}...")
                async with websockets.connect(uri) as websocket:
                    self.websocket = websocket
                    self.running = True
                    logger.info(f"Connected as {self.device_id}")

                    # Start receiving commands in background
                    receive_task = asyncio.create_task(self.receive_commands())

                    # Send packets
                    interval = 1.0 / self.sampling_rate_hz
                    while self.running:
                        packet = self.generate_packet()
                        await websocket.send(json.dumps(packet))

                        if self.sequence % 50 == 0:
                            logger.info(
                                f"Sent {self.sequence} packets "
                                f"(sequence: {packet['sequence']})"
                            )

                        await asyncio.sleep(interval)

            except websockets.ConnectionClosed as e:
                logger.warning(f"Connection closed: {e}")
                self.running = False
                await asyncio.sleep(5)  # Wait before reconnecting
            except ConnectionRefusedError:
                logger.error("Connection refused. Is the server running?")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                self.running = False
                await asyncio.sleep(5)

    def stop(self) -> None:
        """Stop the simulator."""
        self.running = False
        logger.info("Simulator stopping...")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Mock ESP32 simulator for Parkinson's monitoring system"
    )
    parser.add_argument(
        "--device-id",
        default="ESP32_001",
        help="Device identifier (default: ESP32_001)"
    )
    parser.add_argument(
        "--patient-id",
        default="P001",
        help="Patient identifier (default: P001)"
    )
    parser.add_argument(
        "--server-url",
        default="ws://localhost:8000",
        help="Server WebSocket URL (default: ws://localhost:8000)"
    )
    parser.add_argument(
        "--sampling-rate",
        type=int,
        default=50,
        help="Sampling rate in Hz (default: 50)"
    )
    parser.add_argument(
        "--signal-mode",
        choices=["baseline", "tremor_like", "gait_like", "fog_like"],
        default="baseline",
        help="Signal generation mode (default: baseline)"
    )
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_args()

    simulator = MockESP32(
        device_id=args.device_id,
        patient_id=args.patient_id,
        server_url=args.server_url,
        sampling_rate_hz=args.sampling_rate,
        signal_mode=args.signal_mode,
    )

    try:
        await simulator.connect_and_send()
    except KeyboardInterrupt:
        logger.info("Simulator interrupted by user")
    finally:
        simulator.stop()


if __name__ == "__main__":
    asyncio.run(main())
