"""
Health check endpoint for the Parkinson's Monitoring System.

This module provides health check endpoints to verify the system
status, including database connectivity and service health.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from pc_backend.app.core.config import settings
from pc_backend.app.database.session import get_db
from pc_backend.app.websocket.manager import connection_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint returning basic project information.

    Returns:
        Dict with project name, version, and status
    """
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "stage": "Stage 1: Project Foundation",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        Dict with API status, database status, and timestamp
    """
    # Check database connectivity
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    # Get connected devices count
    connected_devices = connection_manager.get_connection_count()

    return {
        "api_status": "healthy",
        "database_status": db_status,
        "connected_devices": connected_devices,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_info": {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "retention_hours": settings.RETENTION_HOURS,
            "default_sampling_rate_hz": settings.DEFAULT_SAMPLING_RATE_HZ,
        },
    }
