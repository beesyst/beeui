from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from beeui_module.pages.models import BeeUiConfig, BeeUiNavigationItem, BeeUiPage

_SAFE_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
_SAFE_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_RESERVED_PATHS = {"/health", "/static"}
_RESERVED_PREFIXES = ("/static/",)


# Загрузка и валидация конфигурации BeeUI из YAML файла
def load_beeui_config(config_path: Path) -> BeeUiConfig:
    if not config_path.is_file():
        raise FileNotFoundError(f"BeeUI schema config is missing: {config_path}")

    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("schema.yml root must be a YAML mapping")

    _validate_exact_keys(payload, {"app", "navigation", "pages"}, "root")

    app_cfg = payload.get("app")
    if not isinstance(app_cfg, dict):
        raise ValueError("Missing required key: app")
    _validate_exact_keys(app_cfg, {"title", "product"}, "app")

    app_title = _required_non_empty_string(app_cfg, "title", "app")
    product = _required_non_empty_string(app_cfg, "product", "app")

    navigation_cfg = payload.get("navigation")
    if not isinstance(navigation_cfg, list):
        raise ValueError("navigation must be a list")

    navigation: list[BeeUiNavigationItem] = []
    for index, item in enumerate(navigation_cfg):
        if not isinstance(item, dict):
            raise ValueError(f"navigation[{index}] must be a mapping")
        _validate_exact_keys(item, {"title", "path", "icon"}, f"navigation[{index}]")

        nav_title = _required_non_empty_string(item, "title", f"navigation[{index}]")
        nav_path = _safe_path(item.get("path"), f"navigation[{index}].path")

        icon = item.get("icon")
        if icon is not None and (not isinstance(icon, str) or not icon.strip()):
            raise ValueError(f"navigation[{index}].icon must be a non-empty string")

        navigation.append(
            BeeUiNavigationItem(title=nav_title, path=nav_path, icon=icon)
        )

    pages_cfg = payload.get("pages")
    if not isinstance(pages_cfg, list):
        raise ValueError("pages must be a list")
    if not pages_cfg:
        raise ValueError("pages must be a non-empty list")

    pages: list[BeeUiPage] = []
    seen_page_ids: set[str] = set()
    seen_page_paths: set[str] = set()

    for index, item in enumerate(pages_cfg):
        if not isinstance(item, dict):
            raise ValueError(f"pages[{index}] must be a mapping")
        _validate_exact_keys(
            item,
            {"id", "path", "title", "subtitle", "blocks"},
            f"pages[{index}]",
        )

        page_id = item.get("id")
        if not isinstance(page_id, str) or not page_id.strip():
            raise ValueError(f"pages[{index}].id must be a non-empty string")
        if not _SAFE_IDENTIFIER_RE.fullmatch(page_id):
            raise ValueError(f"pages[{index}].id must be a safe identifier")
        if page_id in seen_page_ids:
            raise ValueError(f"Duplicate page id: {page_id}")
        seen_page_ids.add(page_id)

        page_path = _safe_path(item.get("path"), f"pages[{index}].path")
        if page_path in seen_page_paths:
            raise ValueError(f"Duplicate page path: {page_path}")
        seen_page_paths.add(page_path)

        page_title = _required_non_empty_string(item, "title", f"pages[{index}]")

        subtitle = item.get("subtitle")
        if subtitle is not None and (
            not isinstance(subtitle, str) or not subtitle.strip()
        ):
            raise ValueError(f"pages[{index}].subtitle must be a non-empty string")

        blocks = item.get("blocks")
        if not isinstance(blocks, list):
            raise ValueError(f"pages[{index}].blocks must be a list")

        pages.append(
            BeeUiPage(
                page_id=page_id,
                path=page_path,
                title=page_title,
                subtitle=subtitle,
                blocks=blocks,
            )
        )

    for nav_item in navigation:
        if nav_item.path not in seen_page_paths:
            raise ValueError(
                f"navigation path must match a declared page path: {nav_item.path}"
            )

    return BeeUiConfig(
        app_title=app_title,
        product=product,
        navigation=navigation,
        pages=pages,
    )


# Регистрация маршрутов для страниц BeeUI на основе конфигурации и префикса маршрута
def _validate_exact_keys(
    payload: dict[str, Any],
    allowed_keys: set[str],
    prefix: str,
) -> None:
    unknown = sorted(set(payload) - allowed_keys)
    if unknown:
        raise ValueError(f"{prefix} contains unsupported keys: {', '.join(unknown)}")


# Чек, что строка является безопасным путем без запрещенных символов и зарезервированных префиксов
def _required_non_empty_string(
    payload: dict[str, Any],
    key: str,
    prefix: str,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{prefix}.{key} must be a non-empty string")
    return value.strip()


# Чек, что строка является безопасным путем без запрещенных символов и зарезервированных префиксов
def _safe_path(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")

    path = value.strip()
    if path == "/":
        return path

    if not path.startswith("/"):
        raise ValueError(f"{field_name} must start with '/'")
    if path.endswith("/"):
        raise ValueError(f"{field_name} must not have a trailing slash")
    if "//" in path or "\\" in path or "?" in path or "#" in path:
        raise ValueError(f"{field_name} must be a safe path")

    segments = path.split("/")[1:]
    for segment in segments:
        if segment in {"", ".", ".."}:
            raise ValueError(f"{field_name} must be a safe path")
        if not _SAFE_SEGMENT_RE.fullmatch(segment):
            raise ValueError(f"{field_name} must be a safe path")

    if path in _RESERVED_PATHS or any(
        path.startswith(prefix) for prefix in _RESERVED_PREFIXES
    ):
        raise ValueError(f"{field_name} uses a reserved path")

    return path
