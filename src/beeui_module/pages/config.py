from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from beeui_module.pages.models import (
    BeeUiConfig,
    BeeUiNavigationItem,
    BeeUiPage,
    LayoutConfig,
    NavbarConfig,
    SidebarConfig,
    ThemeConfig,
)

_SAFE_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
_SAFE_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_RESERVED_PATHS = {"/health", "/static"}
_RESERVED_PREFIXES = ("/static/",)
_THEME_MODES = {"light", "dark", "auto"}
_THEME_PRIMARYS = {
    "blue",
    "azure",
    "cyan",
    "teal",
    "green",
    "lime",
    "yellow",
    "orange",
    "red",
    "pink",
    "indigo",
}
_THEME_BASES = {"slate", "gray", "zinc", "neutral", "stone"}
_THEME_FONTS = {"sans-serif", "serif", "monospace"}
_THEME_RADII = {0, 1, 2}
_THEME_DENSITIES = {"default", "compact", "comfortable"}
_LAYOUT_TYPES = {"vertical"}
_LAYOUT_CONTAINERS = {"xl", "fluid"}
_LAYOUT_SIDEBAR_VARIANTS = {"default", "dark"}
_LAYOUT_NAVBAR_VARIANTS = {"default", "dark"}


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
    _validate_exact_keys(
        app_cfg,
        {"title", "product", "logo_text", "theme", "layout"},
        "app",
    )

    app_title = _required_non_empty_string(app_cfg, "title", "app")
    product = _required_non_empty_string(app_cfg, "product", "app")
    logo_text = _required_non_empty_string(app_cfg, "logo_text", "app")

    theme_cfg = app_cfg.get("theme")
    if not isinstance(theme_cfg, dict):
        raise ValueError("Missing required key: app.theme")
    _validate_exact_keys(
        theme_cfg,
        {"mode", "primary", "base", "font", "radius", "density"},
        "app.theme",
    )
    theme = ThemeConfig(
        mode=_required_enum(theme_cfg, "mode", "app.theme", _THEME_MODES),
        primary=_required_enum(theme_cfg, "primary", "app.theme", _THEME_PRIMARYS),
        base=_required_enum(theme_cfg, "base", "app.theme", _THEME_BASES),
        font=_required_enum(theme_cfg, "font", "app.theme", _THEME_FONTS),
        radius=_required_int_enum(theme_cfg, "radius", "app.theme", _THEME_RADII),
        density=_required_enum(theme_cfg, "density", "app.theme", _THEME_DENSITIES),
    )

    layout_cfg = app_cfg.get("layout")
    if not isinstance(layout_cfg, dict):
        raise ValueError("Missing required key: app.layout")
    _validate_exact_keys(
        layout_cfg,
        {"type", "container", "sidebar", "navbar"},
        "app.layout",
    )

    sidebar_cfg = layout_cfg.get("sidebar")
    if not isinstance(sidebar_cfg, dict):
        raise ValueError("Missing required key: app.layout.sidebar")
    _validate_exact_keys(
        sidebar_cfg,
        {"variant", "collapsed"},
        "app.layout.sidebar",
    )

    navbar_cfg = layout_cfg.get("navbar")
    if not isinstance(navbar_cfg, dict):
        raise ValueError("Missing required key: app.layout.navbar")
    _validate_exact_keys(
        navbar_cfg,
        {"enabled", "variant", "sticky"},
        "app.layout.navbar",
    )

    layout = LayoutConfig(
        type=_required_enum(layout_cfg, "type", "app.layout", _LAYOUT_TYPES),
        container=_required_enum(
            layout_cfg,
            "container",
            "app.layout",
            _LAYOUT_CONTAINERS,
        ),
        sidebar=SidebarConfig(
            variant=_required_enum(
                sidebar_cfg,
                "variant",
                "app.layout.sidebar",
                _LAYOUT_SIDEBAR_VARIANTS,
            ),
            collapsed=_required_bool(sidebar_cfg, "collapsed", "app.layout.sidebar"),
        ),
        navbar=NavbarConfig(
            enabled=_required_bool(navbar_cfg, "enabled", "app.layout.navbar"),
            variant=_required_enum(
                navbar_cfg,
                "variant",
                "app.layout.navbar",
                _LAYOUT_NAVBAR_VARIANTS,
            ),
            sticky=_required_bool(navbar_cfg, "sticky", "app.layout.navbar"),
        ),
    )

    navigation_cfg = payload.get("navigation")
    if not isinstance(navigation_cfg, list):
        raise ValueError("navigation must be a list")

    navigation: list[BeeUiNavigationItem] = []
    seen_nav_paths: set[str] = set()
    for index, item in enumerate(navigation_cfg):
        navigation.append(
            _parse_navigation_item(
                item,
                prefix=f"navigation[{index}]",
                seen_nav_paths=seen_nav_paths,
                seen_page_paths=set(),
            )
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

    for index, item in enumerate(navigation_cfg):
        _validate_navigation_pages(item, f"navigation[{index}]", seen_page_paths)

    return BeeUiConfig(
        app_title=app_title,
        product=product,
        logo_text=logo_text,
        theme=theme,
        layout=layout,
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


# Чек, что значение по ключу является булевым
def _required_bool(payload: dict[str, Any], key: str, prefix: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{prefix}.{key} must be a boolean")
    return value


# Чек, что значение по ключу является строкой и входит в набор разрешенных значений
def _required_enum(
    payload: dict[str, Any],
    key: str,
    prefix: str,
    allowed_values: set[str],
) -> str:
    value = _required_non_empty_string(payload, key, prefix)
    if value not in allowed_values:
        raise ValueError(f"{prefix}.{key} must be one of {sorted(allowed_values)}")
    return value


# Чек, что значение по ключу является целым числом и входит в набор разрешенных значений
def _required_int_enum(
    payload: dict[str, Any],
    key: str,
    prefix: str,
    allowed_values: set[int],
) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or value not in allowed_values:
        raise ValueError(f"{prefix}.{key} must be one of {sorted(allowed_values)}")
    return value


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


# Чек, что строка является безопасным идентификатором без запрещенных символов
def _parse_navigation_item(
    item: Any,
    *,
    prefix: str,
    seen_nav_paths: set[str],
    seen_page_paths: set[str],
) -> BeeUiNavigationItem:
    if not isinstance(item, dict):
        raise ValueError(f"{prefix} must be a mapping")

    _validate_exact_keys(
        item,
        {"title", "path", "icon", "disabled", "children"},
        prefix,
    )

    nav_title = _required_non_empty_string(item, "title", prefix)

    icon = item.get("icon")
    if icon is not None and (not isinstance(icon, str) or not icon.strip()):
        raise ValueError(f"{prefix}.icon must be a non-empty string")

    disabled = item.get("disabled", False)
    if not isinstance(disabled, bool):
        raise ValueError(f"{prefix}.disabled must be a boolean")

    children_cfg = item.get("children", [])
    if not isinstance(children_cfg, list):
        raise ValueError(f"{prefix}.children must be a list")

    if children_cfg and disabled:
        raise ValueError(f"{prefix}.disabled cannot be true when children are defined")

    if children_cfg:
        if item.get("path") is not None:
            raise ValueError(f"{prefix}.path must be omitted when children are defined")
        children = [
            _parse_navigation_item(
                child,
                prefix=f"{prefix}.children[{index}]",
                seen_nav_paths=seen_nav_paths,
                seen_page_paths=seen_page_paths,
            )
            for index, child in enumerate(children_cfg)
        ]
        if not children:
            raise ValueError(f"{prefix}.children must not be empty")
        return BeeUiNavigationItem(
            title=nav_title,
            icon=icon,
            disabled=False,
            children=children,
        )

    raw_path = item.get("path")
    path: str | None = None
    if raw_path is not None:
        path = _safe_path(raw_path, f"{prefix}.path")
        if path in seen_nav_paths:
            raise ValueError(f"Duplicate navigation path: {path}")
        seen_nav_paths.add(path)
        if seen_page_paths and not disabled and path not in seen_page_paths:
            raise ValueError(f"navigation path must match a declared page path: {path}")
    elif not disabled:
        raise ValueError(f"{prefix}.path must be a non-empty string")

    return BeeUiNavigationItem(
        title=nav_title,
        path=path,
        icon=icon,
        disabled=disabled,
    )


# Тест: загрузка конфига с навигационным путем, совпадающим с зарезервированными путями, вызывает ошибку
def _validate_navigation_pages(
    item: Any,
    prefix: str,
    seen_page_paths: set[str],
) -> None:
    if not isinstance(item, dict):
        raise ValueError(f"{prefix} must be a mapping")

    children_cfg = item.get("children", [])
    if not isinstance(children_cfg, list):
        raise ValueError(f"{prefix}.children must be a list")
    if children_cfg:
        for index, child in enumerate(children_cfg):
            _validate_navigation_pages(
                child,
                f"{prefix}.children[{index}]",
                seen_page_paths,
            )
        return

    raw_path = item.get("path")
    disabled = item.get("disabled", False)
    if raw_path is None or disabled:
        return

    path = _safe_path(raw_path, f"{prefix}.path")
    if path not in seen_page_paths:
        raise ValueError(f"navigation path must match a declared page path: {path}")
