"""
Main FastAPI application for the Parkinson's Monitoring System.

This module creates and configures the FastAPI application with all
endpoints, middleware, and lifecycle management.

Application Structure:
- Health check endpoints
- WebSocket endpoints for ESP32 communication
- Database initialization on startup
- Graceful shutdown handling
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pc_backend.app.api.health import router as health_router
from pc_backend.app.core.config import settings
from pc_backend.app.core.logging import setup_logging
from pc_backend.app.database.base import init_database
from pc_backend.app.websocket.sensor_endpoint import router as ws_router

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Initialize database on startup
    - Clean up resources on shutdown
    """
    # Startup
    logger.info("Starting Parkinson's Monitoring System...")
    logger.info(f"App: {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL}")

    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    # Cleanup resources if needed
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Parkinson's Tremor and Freezing of Gait Monitoring & Cueing System. "
            "This API provides WebSocket communication for ESP32 devices with "
            "dual MPU6050 sensors."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(ws_router, tags=["websocket"])

    return app


# Create application instance
app = create_app()
