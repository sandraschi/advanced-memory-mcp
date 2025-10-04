"""Logging configuration for basic-memory."""

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    env: str,
    home_dir: Path,
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    console: bool = True,
) -> None:
    """
    Configure logging for the application.

    Args:
        env: The environment name (dev, test, prod)
        home_dir: The root directory for the application
        log_file: The name of the log file to write to
        log_level: The logging level to use
        console: Whether to log to the console
    """
    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Add file handler if log file is specified and not in test environment
    if log_file and env != "test":
        log_path = home_dir / log_file
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add console handler if requested or in test mode
    if env == "test" or console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Configure third-party loggers
    configure_third_party_loggers(log_level)

def configure_third_party_loggers(log_level: str = "WARNING") -> None:
    """Configure logging levels for third-party libraries."""
    # Reduce noise from third-party libraries
    noisy_loggers = {
        # HTTP client logs
        "httpx": logging.WARNING,
        # File watching logs
        "watchfiles.main": logging.WARNING,
        # SQLAlchemy deprecation warnings
        "sqlalchemy": logging.WARNING,
    }

    # Set log levels for noisy loggers
    for logger_name, level in noisy_loggers.items():
        logging.getLogger(logger_name).setLevel(level)
