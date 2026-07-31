from __future__ import annotations

import ipaddress
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
VALID_COOKIE_SAMESITE_VALUES = frozenset({"lax", "strict", "none"})
MIN_SESSION_MAX_AGE_SECONDS = 60
MAX_SESSION_MAX_AGE_SECONDS = 604800
_FRAME_ORIGIN_SCHEMES = frozenset({"http", "https"})
_FRAME_HOSTNAME_RE = re.compile(
    r"^[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?"
    r"(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)*\.?$"
)
_ENV_REF_RE = re.compile(r"^\$\{([A-Z0-9_]+)\}$")


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
    _validate_auth(payload)
    _validate_features(payload)
    _validate_product(payload)
    _validate_storage(payload)

    return payload


def _validate_app(settings: dict[str, Any]) -> None:
    app = settings.get("app")
    if not isinstance(app, dict):
        raise ValueError("Missing required key: app")

    if app.get("name") != "beeui":
        raise ValueError("settings.yml must declare app.name=beeui")


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

    if "frame_ancestors" in security_cfg:
        frame_ancestors = security_cfg["frame_ancestors"]
        if not isinstance(frame_ancestors, list):
            raise ValueError("security.frame_ancestors must be a list")
        for origin in frame_ancestors:
            if not is_valid_frame_origin(origin):
                raise ValueError(
                    "security.frame_ancestors must contain only absolute "
                    "http(s) origins without path, query, fragment or wildcard"
                )


def is_valid_frame_origin(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if not value or value != value.strip() or any(char.isspace() for char in value):
        return False
    origin = value
    if "*" in origin or "://" not in origin:
        return False
    if origin in {"*", "'self'", "'none'"}:
        return False
    for char in ("?", "#", "@", "\\", ";"):
        if char in origin:
            return False
    try:
        parsed = urlsplit(origin)
        port = parsed.port
    except ValueError:
        return False
    if parsed.scheme not in _FRAME_ORIGIN_SCHEMES:
        return False
    if parsed.username or parsed.password:
        return False
    if parsed.path or parsed.query or parsed.fragment:
        return False
    if parsed.netloc.endswith(":"):
        return False
    host = parsed.hostname
    if not host or not _is_valid_frame_hostname(host):
        return False
    if port is not None and not (1 <= port <= 65535):
        return False
    return True


def _is_valid_frame_hostname(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    return _FRAME_HOSTNAME_RE.fullmatch(host) is not None


def _validate_auth(settings: dict[str, Any]) -> None:
    auth_cfg = settings.get("auth")
    if auth_cfg is None:
        return

    if not isinstance(auth_cfg, dict):
        raise ValueError("auth must be a mapping")

    if "enabled" not in auth_cfg:
        raise ValueError("Missing required key: auth.enabled")

    if not isinstance(auth_cfg["enabled"], bool):
        raise ValueError("auth.enabled must be a boolean")

    cookie_samesite = auth_cfg.get("cookie_samesite", "lax")
    if not isinstance(cookie_samesite, str):
        raise ValueError("auth.cookie_samesite must be a string")
    normalized_samesite = cookie_samesite.strip().lower()
    if normalized_samesite not in VALID_COOKIE_SAMESITE_VALUES:
        raise ValueError(
            "auth.cookie_samesite must be one of "
            f"{sorted(VALID_COOKIE_SAMESITE_VALUES)}"
        )

    session_max_age = auth_cfg.get("session_age_max")
    if session_max_age is not None:
        if isinstance(session_max_age, bool) or not isinstance(session_max_age, int):
            raise ValueError("auth.session_age_max must be an integer")
        if not (
            MIN_SESSION_MAX_AGE_SECONDS
            <= session_max_age
            <= MAX_SESSION_MAX_AGE_SECONDS
        ):
            raise ValueError(
                "auth.session_age_max must be in range "
                f"{MIN_SESSION_MAX_AGE_SECONDS}..{MAX_SESSION_MAX_AGE_SECONDS}"
            )

    if auth_cfg["enabled"]:
        if "cookie_secure" not in auth_cfg:
            raise ValueError(
                "Missing required key: auth.cookie_secure when auth.enabled=true"
            )
        if not isinstance(auth_cfg["cookie_secure"], bool):
            raise ValueError("auth.cookie_secure must be a boolean")

        if normalized_samesite == "none" and auth_cfg["cookie_secure"] is not True:
            raise ValueError(
                "auth.cookie_samesite='none' requires auth.cookie_secure=true"
            )

        for key in ("session_secret", "operator_token", "admin_token"):
            if key not in auth_cfg:
                raise ValueError(
                    f"Missing required key: auth.{key} when auth.enabled=true"
                )

            resolved_value = _resolve_env_ref(auth_cfg[key])
            if not isinstance(resolved_value, str) or not resolved_value.strip():
                raise ValueError(
                    f"auth.{key} must resolve to a non-empty string when auth.enabled=true"
                )


def _resolve_env_ref(value: Any) -> Any:
    if not isinstance(value, str):
        return value

    match = _ENV_REF_RE.fullmatch(value.strip())
    if match is None:
        return value

    env_name = match.group(1)
    return os.environ.get(env_name)


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
