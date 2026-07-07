"""
Logging configuration for the Parkinson's Monitoring System.

This module provides centralized logging setup using loguru for
structured and configurable logging.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from pc_backend.app.core.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
    """
    level = log_level or settings.LOG_LEVEL

    # Remove default handler
    logger.remove()

    # Console handler with color
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="7 days",
        )

    logger.info(f"Logging configured at {level} level")


def get_logger(name: str):
    """
    Get a named logger instance.

    Args:
        name: Logger name (typically module name)

    Returns:
        Logger: Configured logger instance
    """
    return logger.bind(name=name)
