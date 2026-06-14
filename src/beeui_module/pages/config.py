from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml

from beeui_module.blocks.registry import (
    parse_blocks_registry,
    parse_page_block_placements,
)
from beeui_module.core.paths import project_root
from beeui_module.data.models import (
    ALLOWED_STATIC_SOURCE_FORMATS,
    SUPPORTED_DATA_SOURCE_TYPES,
    DataSourceDefinition,
)
from beeui_module.pages.models import (
    ACCORDION_VARIANTS,
    TABS_VARIANTS,
    AccordionComponentConfig,
    BeeUiConfig,
    BeeUiNavigationItem,
    BeeUiPage,
    ComponentConfig,
    LayoutConfig,
    LocaleConfig,
    NavbarConfig,
    PageTabsConfig,
    PageTabsItem,
    SidebarConfig,
    TabsComponentConfig,
    ThemeConfig,
    normalize_accordion_variant,
    normalize_tabs_variant,
)

_SAFE_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
_SAFE_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
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
_RESERVED_PATHS = {
    "/health",
    "/api",
    "/auth",
    "/venues",
    "/login",
    "/logout",
    "/static",
    "/components",
}
_RESERVED_PREFIXES = (
    "/api/",
    "/auth/",
    "/venues/",
    "/static/",
    "/components/",
)


# Загрузка schema.yml и сбор валидированной BeeUiConfig
def load_beeui_config(config_path: Path) -> BeeUiConfig:
    if not config_path.is_file():
        raise FileNotFoundError(f"BeeUI schema config is missing: {config_path}")

    payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("schema.yml root must be a YAML mapping")

    _validate_exact_keys(
        payload,
        {"app", "navigation", "data_sources", "blocks", "pages", "components"},
        "root",
    )

    app_cfg = payload.get("app")
    if not isinstance(app_cfg, dict):
        raise ValueError("Missing required key: app")
    _validate_exact_keys(
        app_cfg,
        {"title", "product", "logo_text", "locale", "theme", "layout"},
        "app",
    )

    app_title = _required_non_empty_string(app_cfg, "title", "app")
    product = _required_non_empty_string(app_cfg, "product", "app")
    logo_text = _required_non_empty_string(app_cfg, "logo_text", "app")

    locale_cfg = app_cfg.get("locale")
    if locale_cfg is not None:
        if not isinstance(locale_cfg, dict):
            raise ValueError("app.locale must be a mapping")
        _validate_exact_keys(
            locale_cfg,
            {"default", "available"},
            "app.locale",
        )
        locale_default = _required_non_empty_string(locale_cfg, "default", "app.locale")
        available_raw = locale_cfg.get("available")
        if not isinstance(available_raw, list) or not available_raw:
            raise ValueError("app.locale.available must be a non-empty list")
        available: list[str] = []
        for idx, lang in enumerate(available_raw):
            if not isinstance(lang, str) or not lang.strip():
                raise ValueError(
                    f"app.locale.available[{idx}] must be a non-empty string"
                )
            available.append(lang.strip())
        if locale_default not in available:
            raise ValueError(
                f"app.locale.default ({locale_default}) must be in app.locale.available"
            )
        locale = LocaleConfig(default=locale_default, available=tuple(available))
    else:
        locale = LocaleConfig()

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

    data_sources = parse_data_sources(
        payload.get("data_sources"),
        root_dir=_resolve_schema_root(config_path),
    )

    blocks = parse_blocks_registry(
        payload.get("blocks"),
        available_source_ids=set(data_sources),
    )

    components = _parse_components(payload.get("components"))

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
            {"id", "path", "title", "subtitle", "blocks", "tabs"},
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

        placements = parse_page_block_placements(
            page_blocks=item.get("blocks"),
            page_index=index,
            available_block_ids=set(blocks),
        )

        page_tabs = _parse_page_tabs(item.get("tabs"), page_id)

        pages.append(
            BeeUiPage(
                page_id=page_id,
                path=page_path,
                title=page_title,
                subtitle=subtitle,
                blocks=placements,
                tabs=page_tabs,
            )
        )

    for index, item in enumerate(navigation_cfg):
        _validate_navigation_pages(item, f"navigation[{index}]", seen_page_paths)

    return BeeUiConfig(
        app_title=app_title,
        product=product,
        logo_text=logo_text,
        locale=locale,
        theme=theme,
        layout=layout,
        navigation=navigation,
        data_sources=data_sources,
        blocks=blocks,
        pages=pages,
        components=components,
    )


# Парсинг одного block placement и чек ссылки на объявленный block id
def parse_data_sources(
    data_sources_payload: Any,
    *,
    root_dir: Path,
) -> dict[str, DataSourceDefinition]:
    if data_sources_payload is None:
        return {}
    if not isinstance(data_sources_payload, dict):
        raise ValueError("data_sources must be a mapping")

    data_sources: dict[str, DataSourceDefinition] = {}
    for source_id, source_payload in data_sources_payload.items():
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("data_sources keys must be non-empty strings")
        if not _SAFE_IDENTIFIER_RE.fullmatch(source_id):
            raise ValueError(f"data_sources.{source_id} must be a safe identifier")
        if not isinstance(source_payload, dict):
            raise ValueError(f"data_sources.{source_id} must be a mapping")

        source_type = _required_non_empty_string(
            source_payload,
            "type",
            f"data_sources.{source_id}",
        )
        if source_type not in SUPPORTED_DATA_SOURCE_TYPES:
            raise ValueError(
                f"data_sources.{source_id}.type must be one of {sorted(SUPPORTED_DATA_SOURCE_TYPES)}"
            )

        if source_type == "demo":
            _validate_exact_keys(source_payload, {"type"}, f"data_sources.{source_id}")
            data_sources[source_id] = DataSourceDefinition(
                source_id=source_id,
                source_type=source_type,
                root_dir=root_dir,
            )
            continue

        _validate_exact_keys(
            source_payload,
            {"type", "format", "path"},
            f"data_sources.{source_id}",
        )
        source_format = _required_non_empty_string(
            source_payload,
            "format",
            f"data_sources.{source_id}",
        )
        if source_format not in ALLOWED_STATIC_SOURCE_FORMATS:
            raise ValueError(
                f"data_sources.{source_id}.format must be one of {sorted(ALLOWED_STATIC_SOURCE_FORMATS)}"
            )
        source_path = _required_non_empty_string(
            source_payload,
            "path",
            f"data_sources.{source_id}",
        )
        _validate_static_source_path(
            source_path,
            source_format=source_format,
            field_name=f"data_sources.{source_id}.path",
        )
        data_sources[source_id] = DataSourceDefinition(
            source_id=source_id,
            source_type=source_type,
            format=source_format,
            path=source_path,
            root_dir=root_dir,
        )

    return data_sources


# Парсинг components конфига
def _parse_components(payload: Any) -> ComponentConfig:
    if payload is None:
        return ComponentConfig()

    if not isinstance(payload, dict):
        raise ValueError("components must be a mapping")
    _validate_exact_keys(payload, {"tabs", "accordion"}, "components")

    tabs = TabsComponentConfig()
    if "tabs" in payload:
        tabs_cfg = payload["tabs"]
        if not isinstance(tabs_cfg, dict):
            raise ValueError("components.tabs must be a mapping")
        _validate_exact_keys(tabs_cfg, {"variant"}, "components.tabs")
        variant_raw = tabs_cfg.get("variant", "default")
        try:
            variant = normalize_tabs_variant(variant_raw)
        except ValueError as exc:
            raise ValueError(
                f"components.tabs.variant must be one of {sorted(TABS_VARIANTS)}, got: {variant_raw}"
            ) from exc
        tabs = TabsComponentConfig(variant=variant)

    accordion = AccordionComponentConfig()
    if "accordion" in payload:
        acc_cfg = payload["accordion"]
        if not isinstance(acc_cfg, dict):
            raise ValueError("components.accordion must be a mapping")
        _validate_exact_keys(acc_cfg, {"variant"}, "components.accordion")
        variant_raw = acc_cfg.get("variant", "default")
        try:
            variant = normalize_accordion_variant(variant_raw)
        except ValueError as exc:
            raise ValueError(
                f"components.accordion.variant must be one of {sorted(ACCORDION_VARIANTS)}, got: {variant_raw}"
            ) from exc
        accordion = AccordionComponentConfig(variant=variant)

    return ComponentConfig(tabs=tabs, accordion=accordion)


# Парсинг page-level tabs config
def _parse_page_tabs(payload: Any, page_id: str) -> PageTabsConfig | None:
    if payload is None:
        return None

    if not isinstance(payload, dict):
        raise ValueError(f"pages.{page_id}.tabs must be a mapping")
    _validate_exact_keys(
        payload, {"variant", "active_param", "items"}, f"pages.{page_id}.tabs"
    )

    variant_raw = payload.get("variant", "default")
    try:
        variant = normalize_tabs_variant(variant_raw)
    except ValueError as exc:
        raise ValueError(
            f"pages.{page_id}.tabs.variant must be one of {sorted(TABS_VARIANTS)}, got: {variant_raw}"
        ) from exc

    active_param = payload.get("active_param", "tab")
    if (
        not isinstance(active_param, str)
        or not active_param.strip()
        or not _SAFE_IDENTIFIER_RE.fullmatch(active_param.strip())
    ):
        raise ValueError(
            f"pages.{page_id}.tabs.active_param must be a safe query parameter"
        )
    active_param = active_param.strip()

    items_raw = payload.get("items")
    if not isinstance(items_raw, list):
        raise ValueError(f"pages.{page_id}.tabs.items must be a list")

    items: list[PageTabsItem] = []
    seen_ids: set[str] = set()
    for idx, item_raw in enumerate(items_raw):
        if not isinstance(item_raw, dict):
            raise ValueError(f"pages.{page_id}.tabs.items[{idx}] must be a mapping")
        _validate_exact_keys(
            item_raw,
            {"id", "title", "href", "disabled"},
            f"pages.{page_id}.tabs.items[{idx}]",
        )

        tab_id = item_raw.get("id")
        if not isinstance(tab_id, str) or not tab_id.strip():
            raise ValueError(
                f"pages.{page_id}.tabs.items[{idx}].id must be a non-empty string"
            )
        if not _SAFE_IDENTIFIER_RE.fullmatch(tab_id):
            raise ValueError(
                f"pages.{page_id}.tabs.items[{idx}].id must be a safe identifier"
            )
        if tab_id in seen_ids:
            raise ValueError(f"Duplicate tab id in page {page_id}: {tab_id}")
        seen_ids.add(tab_id)

        title = item_raw.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                f"pages.{page_id}.tabs.items[{idx}].title must be a non-empty string"
            )

        href = _validate_tab_href(item_raw.get("href"), page_id, idx)

        disabled = item_raw.get("disabled", False)
        if not isinstance(disabled, bool):
            raise ValueError(
                f"pages.{page_id}.tabs.items[{idx}].disabled must be a boolean"
            )

        items.append(
            PageTabsItem(tab_id=tab_id, title=title, href=href, disabled=disabled)
        )

    return PageTabsConfig(
        variant=variant, active_param=active_param, items=tuple(items)
    )


# Валидация tab href — только safe internal links
def _validate_tab_href(href: Any, page_id: str, idx: int) -> str:
    if not isinstance(href, str) or not href.strip():
        raise ValueError(
            f"pages.{page_id}.tabs.items[{idx}].href must be a non-empty string"
        )

    value = href.strip()
    parsed = urlsplit(value)

    if parsed.scheme or parsed.netloc or value.startswith("//"):
        raise ValueError(
            f"pages.{page_id}.tabs.items[{idx}].href must be an internal link"
        )
    if parsed.fragment:
        raise ValueError(
            f"pages.{page_id}.tabs.items[{idx}].href must not contain fragment"
        )
    if not parsed.path.startswith("/"):
        raise ValueError(f"pages.{page_id}.tabs.items[{idx}].href must start with '/'")

    decoded_value = unquote(value)
    decoded_path = unquote(parsed.path)

    if "\\" in value or "\\" in decoded_value:
        raise ValueError(
            f"pages.{page_id}.tabs.items[{idx}].href must be a safe internal link"
        )
    if any(ord(char) < 32 for char in value + decoded_value):
        raise ValueError(
            f"pages.{page_id}.tabs.items[{idx}].href contains control characters"
        )
    if "//" in parsed.path:
        raise ValueError(
            f"pages.{page_id}.tabs.items[{idx}].href must be a safe internal link"
        )
    if any(segment in {".", ".."} for segment in decoded_path.split("/")):
        raise ValueError(
            f"pages.{page_id}.tabs.items[{idx}].href must not contain traversal"
        )

    return value


# Разрешение блока из реестра по его id и сбор модели для передачи в template, включая разрешение селекторов данных
def _resolve_schema_root(config_path: Path) -> Path:
    if config_path.parent.name == "config":
        return config_path.parent.parent.resolve()

    try:
        return project_root(config_path).resolve()
    except FileNotFoundError:
        return project_root().resolve()


# Валидация и безопасное разрешение пути для static источников
def _validate_static_source_path(
    value: str,
    *,
    source_format: str,
    field_name: str,
) -> None:
    raw_path = Path(value)
    if raw_path.is_absolute() or ".." in raw_path.parts:
        raise ValueError(f"{field_name} must be a safe relative path")

    suffixes = [suffix.lower() for suffix in raw_path.suffixes]
    if source_format == "yaml" and suffixes[-1:] not in [[".yaml"], [".yml"]]:
        raise ValueError(f"{field_name} must match format yaml")
    if source_format == "json" and suffixes[-1:] != [".json"]:
        raise ValueError(f"{field_name} must match format json")


# Чек, что mapping содержит только поля текущего schema contract
def _validate_exact_keys(
    payload: dict[str, Any],
    allowed_keys: set[str],
    prefix: str,
) -> None:
    unknown = sorted(set(payload) - allowed_keys)
    if unknown:
        raise ValueError(f"{prefix} contains unsupported keys: {', '.join(unknown)}")


# Чтение обязательных boolean-полей
def _required_bool(payload: dict[str, Any], key: str, prefix: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{prefix}.{key} must be a boolean")
    return value


# Чтение обязательной строки из заранее разрешенного набора
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


# Чтение обязательного integer-поля из заранее разрешенного набора
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


# Чтение обязательной непустой строки и обрезка внешних пробелов
def _required_non_empty_string(
    payload: dict[str, Any],
    key: str,
    prefix: str,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{prefix}.{key} must be a non-empty string")
    return value.strip()


# Валидация внутренней route path без traversal, query/hash и reserved paths
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


# Валидация одного navigation item и рекурсивный сбор children
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


# Чек, что navigation links указывает на объявленные страницы
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
