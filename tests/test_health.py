"""
Tests for health check endpoints.

This module tests the health check and root endpoints of the
FastAPI application.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(test_client: TestClient):
    """Test root endpoint returns project information."""
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"
    assert "stage" in data


def test_health_endpoint(test_client: TestClient):
    """Test health endpoint returns system status."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "api_status" in data
    assert "database_status" in data
    assert "connected_devices" in data
    assert "timestamp" in data
    assert data["api_status"] == "healthy"
    assert data["database_status"] == "connected"
    assert data["connected_devices"] == 0


def test_health_endpoint_uptime_info(test_client: TestClient):
    """Test health endpoint includes uptime information."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "uptime_info" in data
    assert "app_name" in data["uptime_info"]
    assert "app_version" in data["uptime_info"]
    assert "retention_hours" in data["uptime_info"]
    assert "default_sampling_rate_hz" in data["uptime_info"]
