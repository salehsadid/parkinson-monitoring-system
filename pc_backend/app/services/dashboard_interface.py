"""
Dashboard interface for future caregiver-facing application.

This module provides a no-op implementation of the dashboard interface
that will be used for caregiver notifications in future stages.

Stage 1 Purpose:
- Define interface methods for future implementation
- Provide no-op implementation for testing
- Document expected functionality

Future Implementation:
- Blynk integration for mobile dashboard
- Custom web application
- Real-time event notifications
- Historical data visualization
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DashboardInterface(ABC):
    """
    Abstract interface for caregiver dashboard integration.

    This interface defines the contract for publishing events
    and status updates to a caregiver-facing dashboard.
    """

    @abstractmethod
    def publish_tremor_result(
        self,
        patient_id: str,
        predicted_class: str,
        confidence: Optional[float],
        model_version: str,
    ) -> bool:
        """
        Publish tremor analysis result to dashboard.

        Args:
            patient_id: Patient identifier
            predicted_class: Predicted tremor class
            confidence: Confidence score (0.0 to 1.0) or None
            model_version: ML model version used

        Returns:
            bool: True if published successfully
        """
        raise NotImplementedError("Dashboard publishing not implemented in Stage 1")

    @abstractmethod
    def publish_fog_event(
        self,
        patient_id: str,
        confidence: float,
        cue_triggered: bool,
        model_version: str,
    ) -> bool:
        """
        Publish FOG detection event to dashboard.

        Args:
            patient_id: Patient identifier
            confidence: FOG detection confidence
            cue_triggered: Whether buzzer cue was triggered
            model_version: ML model version used

        Returns:
            bool: True if published successfully
        """
        raise NotImplementedError("Dashboard publishing not implemented in Stage 1")

    @abstractmethod
    def publish_device_status(
        self,
        device_id: str,
        patient_id: str,
        is_connected: bool,
        last_seen: Optional[str] = None,
    ) -> bool:
        """
        Publish device status update to dashboard.

        Args:
            device_id: ESP32 device identifier
            patient_id: Patient identifier
            is_connected: Whether device is currently connected
            last_seen: Optional timestamp of last communication

        Returns:
            bool: True if published successfully
        """
        raise NotImplementedError("Dashboard publishing not implemented in Stage 1")


class NoOpDashboard(DashboardInterface):
    """
    No-op implementation of the dashboard interface.

    This implementation logs all publish attempts but does not
    actually send data to any external service. It is used for
    testing and development purposes.
    """

    def publish_tremor_result(
        self,
        patient_id: str,
        predicted_class: str,
        confidence: Optional[float],
        model_version: str,
    ) -> bool:
        """
        Log tremor result (no-op implementation).

        Args:
            patient_id: Patient identifier
            predicted_class: Predicted tremor class
            confidence: Confidence score or None
            model_version: ML model version used

        Returns:
            bool: Always True (simulated success)
        """
        logger.info(
            f"[NoOp Dashboard] Tremor result for {patient_id}: "
            f"class={predicted_class}, confidence={confidence}, "
            f"model={model_version}"
        )
        return True

    def publish_fog_event(
        self,
        patient_id: str,
        confidence: float,
        cue_triggered: bool,
        model_version: str,
    ) -> bool:
        """
        Log FOG event (no-op implementation).

        Args:
            patient_id: Patient identifier
            confidence: FOG detection confidence
            cue_triggered: Whether buzzer cue was triggered
            model_version: ML model version used

        Returns:
            bool: Always True (simulated success)
        """
        logger.info(
            f"[NoOp Dashboard] FOG event for {patient_id}: "
            f"confidence={confidence:.2f}, cue_triggered={cue_triggered}, "
            f"model={model_version}"
        )
        return True

    def publish_device_status(
        self,
        device_id: str,
        patient_id: str,
        is_connected: bool,
        last_seen: Optional[str] = None,
    ) -> bool:
        """
        Log device status (no-op implementation).

        Args:
            device_id: ESP32 device identifier
            patient_id: Patient identifier
            is_connected: Whether device is currently connected
            last_seen: Optional timestamp of last communication

        Returns:
            bool: Always True (simulated success)
        """
        logger.info(
            f"[NoOp Dashboard] Device status: {device_id} ({patient_id}) - "
            f"connected={is_connected}, last_seen={last_seen}"
        )
        return True


# Global dashboard instance (no-op for Stage 1)
dashboard = NoOpDashboard()
