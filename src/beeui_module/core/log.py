from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from beeui_module.core.paths import log_file_path


# Настройка логирования для приложения
def _parse_level(level: str | int) -> int:
    if isinstance(level, int):
        return level

    resolved = logging.getLevelName(level.upper())
    if isinstance(resolved, int):
        return resolved

    raise ValueError(f"Unsupported log level: {level}")


# Конфигурация логирования, создающая логгер с консольным и файловым обработчиками
def configure_logging(
    *,
    root: Path | str | None = None,
    level: str | int = "INFO",
    utc: bool = True,
    clear_logs: bool = True,
    log_file: str = "logs/app.log",
) -> logging.Logger:
    logger = logging.getLogger("beeui")
    logger.setLevel(_parse_level(level))
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] - [%(name)s] %(message)s"
    )
    if utc:
        formatter.converter = time.gmtime

    log_path = log_file_path(root, log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if clear_logs and log_path.exists():
        log_path.unlink()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
