"""Central logging configuration for Sereni."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

DEFAULT_MAX_BYTES = 1_000_000
DEFAULT_BACKUP_COUNT = 5


def setup_logging(
    app_name: str = "sereni",
    log_dir: str | Path = "logs",
    crisis_dir: str | Path = "logs/crisis",
    level: int = logging.INFO,
) -> tuple[logging.Logger, logging.Logger]:
    """Configure standard and crisis loggers.

    Returns:
        (app_logger, crisis_logger)
    """

    log_dir = Path(log_dir)
    crisis_dir = Path(crisis_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    crisis_dir.mkdir(parents=True, exist_ok=True)

    app_logger = logging.getLogger(app_name)
    crisis_logger = logging.getLogger(f"{app_name}.crisis")

    _configure_handler(
        app_logger,
        log_dir / f"{app_name}.log",
        level=level,
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    # Crisis logs should stand out and be isolated for monitoring/alerting.
    _configure_handler(
        crisis_logger,
        crisis_dir / f"{app_name}_crisis.log",
        level=logging.WARNING,
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    return app_logger, crisis_logger


def _configure_handler(
    logger: logging.Logger,
    file_path: Path,
    *,
    level: int,
    fmt: str,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
    propagate: bool = False,
) -> None:
    handler = RotatingFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt, "%Y-%m-%d %H:%M:%S"))

    if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == str(file_path) for h in logger.handlers):
        logger.addHandler(handler)

    logger.setLevel(level)
    logger.propagate = propagate
