"""
Tests for cue service functionality.

This module tests the CueService class for FOG buzzer activation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pc_backend.app.services.cue_service import CueService
from pc_backend.app.schemas.commands import CommandType


@pytest.fixture
def cue_service():
    """Create a CueService instance for testing."""
    return CueService()


class TestCueService:
    """Tests for CueService class."""

    def test_initial_state(self, cue_service):
        """Test cue service initial state."""
        assert cue_service.get_all_active_cues() == {}
        assert cue_service.is_cue_active("ESP32_001") is False

    def test_get_active_cue_none(self, cue_service):
        """Test getting active cue for non-existent device."""
        assert cue_service.get_active_cue("ESP32_001") is None

    def test_is_cue_active_false(self, cue_service):
        """Test is_cue_active returns False for unknown device."""
        assert cue_service.is_cue_active("ESP32_001") is False

    @pytest.mark.asyncio
    async def test_trigger_fog_cue_device_not_connected(self, cue_service):
        """Test triggering FOG cue when device is not connected."""
        with patch("pc_backend.app.services.cue_service.connection_manager") as mock_manager:
            mock_manager.is_connected.return_value = False

            result = await cue_service.trigger_fog_cue(
                device_id="ESP32_001",
                patient_id="P001",
                confidence=0.91,
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_stop_fog_cue_device_not_connected(self, cue_service):
        """Test stopping FOG cue when device is not connected."""
        with patch("pc_backend.app.services.cue_service.connection_manager") as mock_manager:
            mock_manager.is_connected.return_value = False

            result = await cue_service.stop_fog_cue("ESP32_001")

            assert result is None

    @pytest.mark.asyncio
    async def test_send_ping_device_not_connected(self, cue_service):
        """Test sending ping when device is not connected."""
        with patch("pc_backend.app.services.cue_service.connection_manager") as mock_manager:
            mock_manager.is_connected.return_value = False

            result = await cue_service.send_ping("ESP32_001")

            assert result is None

    def test_get_all_active_cues_empty(self, cue_service):
        """Test getting all active cues when none exist."""
        cues = cue_service.get_all_active_cues()
        assert cues == {}
