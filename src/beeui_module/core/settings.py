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
    _validate_web(payload)
    _validate_logging(payload)
    _validate_security(payload)
    _validate_features(payload)
    _validate_product(payload)
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


# Валидация секции web с проверкой наличия ключей и типов значений
def _validate_web(settings: dict[str, Any]) -> None:
    web_cfg = settings.get("web")
    if not isinstance(web_cfg, dict):
        raise ValueError("Missing required key: web")

    for key in ("host", "port", "route_prefix", "cache_static"):
        if key not in web_cfg:
            raise ValueError(f"Missing required key: web.{key}")

    host = web_cfg["host"]
    if not isinstance(host, str) or not host.strip():
        raise ValueError("web.host must be a non-empty string")

    port = web_cfg["port"]
    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError("web.port must be an integer in range 1..65535")

    route_prefix = web_cfg["route_prefix"]
    if not isinstance(route_prefix, str):
        raise ValueError("web.route_prefix must be a string")
    if route_prefix and ".." in route_prefix.split("/"):
        raise ValueError("web.route_prefix must be a safe URL prefix")

    cache_static = web_cfg["cache_static"]
    if not isinstance(cache_static, int) or cache_static < 0:
        raise ValueError("web.cache_static must be an integer >= 0")


# Валидация секции security с проверкой наличия ключей и типов значений
def _validate_security(settings: dict[str, Any]) -> None:
    security_cfg = settings.get("security")
    if not isinstance(security_cfg, dict):
        raise ValueError("Missing required key: security")

    for key in ("html_autoescape", "assets_ext"):
        if key not in security_cfg:
            raise ValueError(f"Missing required key: security.{key}")

    if security_cfg["html_autoescape"] is not True:
        raise ValueError("security.html_autoescape must be true")
    if not isinstance(security_cfg["assets_ext"], bool):
        raise ValueError("security.assets_ext must be a boolean")


def _validate_features(settings: dict[str, Any]) -> None:
    features_cfg = settings.get("features")
    if not isinstance(features_cfg, dict):
        raise ValueError("Missing required key: features")

    required_keys = (
        "browser_artifact",
        "config_preview",
        "config_apply",
        "operator_actions",
        "api",
    )
    for key in required_keys:
        if key not in features_cfg:
            raise ValueError(f"Missing required key: features.{key}")
        if not isinstance(features_cfg[key], bool):
            raise ValueError(f"features.{key} must be a boolean")


# Валидация секции product с проверкой наличия ключей и типов значений
def _validate_product(settings: dict[str, Any]) -> None:
    product_cfg = settings.get("product")
    if not isinstance(product_cfg, dict):
        raise ValueError("Missing required key: product")

    for key in ("id", "title"):
        if key not in product_cfg:
            raise ValueError(f"Missing required key: product.{key}")

    product_id = product_cfg["id"]
    if not isinstance(product_id, str) or not product_id.strip():
        raise ValueError("product.id must be a non-empty string")

    product_title = product_cfg["title"]
    if not isinstance(product_title, str) or not product_title.strip():
        raise ValueError("product.title must be a non-empty string")


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
