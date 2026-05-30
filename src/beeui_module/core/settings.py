from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


# Загрузка YAML-настроек BeeUI с минимальной fail-fast валидацией
def load_settings(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise FileNotFoundError(f"Settings config is missing: {config_path}")

    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("settings.yml must be a YAML mapping")

    _validate_app(payload)
    _validate_logging(payload)
    _validate_storage(payload)

    return payload


# Валидация структуры и типов в секциях app, logging и storage настроек
def _validate_app(settings: dict[str, Any]) -> None:
    app = settings.get("app")
    if not isinstance(app, dict):
        raise ValueError("Missing required key: app")

    if app.get("name") != "beeui":
        raise ValueError("settings.yml must declare app.name=beeui")


# Валидация секции logging с проверкой наличия ключей и типов значений
def _validate_logging(settings: dict[str, Any]) -> None:
    logging_cfg = settings.get("logging")
    if not isinstance(logging_cfg, dict):
        raise ValueError("Missing required key: logging")

    for key in ("clear_logs", "utc", "level", "file"):
        if key not in logging_cfg:
            raise ValueError(f"Missing required key: logging.{key}")

    if not isinstance(logging_cfg["clear_logs"], bool):
        raise ValueError("logging.clear_logs must be a boolean")

    if not isinstance(logging_cfg["utc"], bool):
        raise ValueError("logging.utc must be a boolean")

    if logging_cfg["level"] not in VALID_LOG_LEVELS:
        raise ValueError(f"logging.level must be one of {sorted(VALID_LOG_LEVELS)}")

    log_file = logging_cfg["file"]
    if not isinstance(log_file, str) or not log_file.strip():
        raise ValueError("logging.file must be a non-empty string")

    log_file_path = Path(log_file)
    if log_file_path.is_absolute() or ".." in log_file_path.parts:
        raise ValueError("logging.file must be a safe relative path")


# Валидация секции storage с проверкой наличия ключей и типов значений
def _validate_storage(settings: dict[str, Any]) -> None:
    storage_cfg = settings.get("storage")
    if not isinstance(storage_cfg, dict):
        raise ValueError("Missing required key: storage")

    for key in ("enabled", "root"):
        if key not in storage_cfg:
            raise ValueError(f"Missing required key: storage.{key}")

    if not isinstance(storage_cfg["enabled"], bool):
        raise ValueError("storage.enabled must be a boolean")

    storage_root = storage_cfg["root"]
    if not isinstance(storage_root, str) or not storage_root.strip():
        raise ValueError("storage.root must be a non-empty string")

    storage_root_path = Path(storage_root)
    if storage_root_path.is_absolute() or ".." in storage_root_path.parts:
        raise ValueError("storage.root must be a safe relative path")
