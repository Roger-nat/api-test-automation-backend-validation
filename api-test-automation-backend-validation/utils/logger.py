from __future__ import annotations

import logging
from pathlib import Path

from app.config import ROOT_DIR


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_dir = ROOT_DIR / "artifacts" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.FileHandler(log_dir / "test-framework.log", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
