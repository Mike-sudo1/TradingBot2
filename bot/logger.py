"""Loguru logger setup."""
from __future__ import annotations

from loguru import logger
from pathlib import Path
from datetime import datetime
from .config import Config


def get_logger(config: Config):
    logger.remove()
    level = "DEBUG" if config.DEBUG else "INFO"
    logger.add(lambda msg: print(msg, end=""), level=level)
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"trading_{datetime.utcnow().date()}.log"
    logger.add(log_file, rotation="1 day", level=level)
    return logger


__all__ = ["get_logger"]
