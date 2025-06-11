"""
Simple logging configuration for Slack AI Assistant
"""
import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """Setup basic logging"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("slack_bolt").setLevel(logging.WARNING)
    logging.getLogger("slack_sdk").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)


# Create default logger for imports
logger = get_logger(__name__)