"""Utility functions for the database agent."""

import logging
import json
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("database_agent.log"),
            logging.StreamHandler(),
        ],
    )
    logger.info(f"Logging initialized with level {log_level}")


def format_query_result(data: Dict[str, Any]) -> str:
    """Format query result for display.

    Args:
        data: Dictionary with query result

    Returns:
        Formatted string representation
    """
    if not data:
        return "No results"

    lines = []
    for key, value in data.items():
        lines.append(f"{key}: {value}")

    return "\n".join(lines)


def load_env_file(path: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file.

    Args:
        path: Path to .env file

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
        logger.info(f"Loaded {len(env_vars)} environment variables from {path}")
    except FileNotFoundError:
        logger.warning(f"Environment file not found: {path}")

    return env_vars


def save_result_to_json(data: Dict[str, Any], filename: str) -> None:
    """Save query result to JSON file.

    Args:
        data: Data to save
        filename: Output filename
    """
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Result saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save result: {e}")


def get_timestamp() -> str:
    """Get current timestamp in ISO format.

    Returns:
        Current timestamp
    """
    return datetime.now().isoformat()
