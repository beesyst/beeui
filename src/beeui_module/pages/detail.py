from __future__ import annotations

from typing import Any
from urllib.parse import unquote, urlsplit

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from beeui_module.pages.links import (
    add_preserved_params_to_href,
    is_safe_internal_href,
    preserve_allowed_params,
)
from beeui_module.pages.locale import resolve_localized_text
from beeui_module.pages.models import BeeUiConfig
from beeui_module.pages.router import (
    _build_language_switcher,
    build_components_context,
    build_layout_context,
    build_navigation,
    build_shell_classes,
    build_theme_context,
    resolve_locale,
)

ALLOWED_SECTION_KINDS: frozenset[str] = frozenset(
    {"key_value", "text", "table", "links"}
)


def _validate_internal_href(href: Any) -> str | None:
    if not isinstance(href, str):
        return None

    value = href.strip()
    if not value:
        return None
    if not value.startswith("/"):
        return None
    if "\\" in value:
        return None
    if not is_safe_internal_href(value):
        return None

    try:
        parsed = urlsplit(value)
    except Exception:
        return None

    decoded_path = unquote(parsed.path)
    if "\\" in decoded_path:
        return None
    if "//" in decoded_path:
        return None
    if any(part in {".", ".."} for part in decoded_path.split("/")):
        return None

    return value


def _detail_preserved_params(
    request: Request,
    locale: str,
    default_locale: str,
) -> dict[str, str]:
    params = preserve_allowed_params(dict(request.query_params))
    if locale == default_locale:
        params.pop("lang", None)
    else:
        params["lang"] = locale
    return params


def _apply_preserved_params_to_sections(
    sections: list[dict[str, Any]],
    current_params: dict[str, str],
) -> list[dict[str, Any]]:
    updated_sections: list[dict[str, Any]] = []
    for section in sections:
        if section.get("kind") != "links":
            updated_sections.append(section)
            continue

        items: list[dict[str, str]] = []
        for item in section.get("items", []):
            if not isinstance(item, dict):
                continue
            href = item.get("href", "")
            if href:
                href = add_preserved_params_to_href(href, current_params)
            items.append(
                {
                    "label": _display_value(item.get("label")),
                    "href": href,
                }
            )

        updated_sections.append(
            {
                "kind": "links",
                "title": section.get("title", ""),
                "items": items,
            }
        )

    return updated_sections


def _display_value(value: Any, default: str = "n/a") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        clean = value.strip()
        if clean.lower() in {"", "none", "null"}:
            return default
        return clean
    if isinstance(value, (int, float, bool)):
        return str(value)
    return default


def _normalize_key_value_section(section: dict[str, Any]) -> dict[str, Any] | None:
    raw_items = section.get("items")
    if not isinstance(raw_items, list):
        return None
    items: list[dict[str, str]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "label": _display_value(item.get("label")),
                "value": _display_value(item.get("value")),
            }
        )
    if not items:
        return None
    return {
        "kind": "key_value",
        "title": _display_value(section.get("title"), default=""),
        "items": items,
    }


def _normalize_text_section(section: dict[str, Any]) -> dict[str, Any] | None:
    body = section.get("body")
    if body is None:
        return None
    return {
        "kind": "text",
        "title": _display_value(section.get("title"), default=""),
        "body": _display_value(body),
    }


def _normalize_table_section(section: dict[str, Any]) -> dict[str, Any] | None:
    raw_columns = section.get("columns")
    if not isinstance(raw_columns, list) or not raw_columns:
        return None
    raw_rows = section.get("rows")
    if not isinstance(raw_rows, list):
        return None

    columns: list[dict[str, str]] = []
    for col in raw_columns:
        if not isinstance(col, dict):
            continue
        key = col.get("key")
        if not isinstance(key, str) or not key.strip():
            continue
        columns.append(
            {
                "key": key.strip(),
                "label": _display_value(col.get("label"), default=key.strip()),
            }
        )
    if not columns:
        return None

    rows: list[dict[str, str]] = []
    for row in raw_rows:
        if not isinstance(row, dict):
            continue
        safe_row: dict[str, str] = {}
        for col in columns:
            safe_row[col["key"]] = _display_value(row.get(col["key"]))
        rows.append(safe_row)

    return {
        "kind": "table",
        "title": _display_value(section.get("title"), default=""),
        "columns": columns,
        "rows": rows,
    }


def _normalize_links_section(section: dict[str, Any]) -> dict[str, Any] | None:
    raw_items = section.get("items")
    if not isinstance(raw_items, list):
        return None
    items: list[dict[str, str]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        href = _validate_internal_href(item.get("href"))
        if href is None:
            items.append(
                {
                    "label": _display_value(item.get("label")),
                    "href": "",
                }
            )
        else:
            items.append(
                {
                    "label": _display_value(item.get("label")),
                    "href": href,
                }
            )
    if not items:
        return None
    return {
        "kind": "links",
        "title": _display_value(section.get("title"), default=""),
        "items": items,
    }


_SECTION_NORMALIZERS: dict[str, Any] = {
    "key_value": _normalize_key_value_section,
    "text": _normalize_text_section,
    "table": _normalize_table_section,
    "links": _normalize_links_section,
}


def normalize_sections(
    raw_sections: list[dict[str, Any]] | Any,
) -> list[dict[str, Any]]:
    if not isinstance(raw_sections, list):
        return []
    normalized: list[dict[str, Any]] = []
    for section in raw_sections:
        if not isinstance(section, dict):
            continue
        kind = section.get("kind")
        if kind not in ALLOWED_SECTION_KINDS:
            continue
        normalizer = _SECTION_NORMALIZERS.get(kind)
        if normalizer is None:
            continue
        result = normalizer(section)
        if result is not None:
            normalized.append(result)
    return normalized


def normalize_detail_page(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {
            "page_id": "",
            "title": "Unavailable",
            "subtitle": None,
            "back_href": None,
            "warnings": [],
            "sections": [],
        }

    raw_warnings = raw.get("warnings")
    safe_warnings: list[str] = []
    if isinstance(raw_warnings, list):
        for w in raw_warnings:
            if isinstance(w, str):
                safe_warnings.append(w)

    safe_back_href = _validate_internal_href(raw.get("back_href"))

    raw_sections = raw.get("sections")
    sections = normalize_sections(raw_sections)

    return {
        "page_id": _display_value(raw.get("page_id")),
        "title": _display_value(raw.get("title"), default="Detail"),
        "subtitle": _display_value(raw.get("subtitle"), default="")
        if raw.get("subtitle") is not None
        else None,
        "back_href": safe_back_href,
        "warnings": safe_warnings,
        "sections": sections,
    }


def render_beeui_detail_page(
    request: Request,
    page: dict[str, Any],
    *,
    templates: Jinja2Templates,
    route_prefix: str,
    ui_config: BeeUiConfig,
    product_title: str,
    product_id: str,
) -> HTMLResponse:
    normalized = normalize_detail_page(page)

    locale = resolve_locale(request, ui_config.locale)
    theme = build_theme_context(ui_config)
    layout = build_layout_context(ui_config)
    shell_classes = build_shell_classes(theme, layout)
    current_params = _detail_preserved_params(request, locale, ui_config.locale.default)

    back_href = normalized["back_href"]
    if back_href:
        back_href = add_preserved_params_to_href(back_href, current_params)

    sections = _apply_preserved_params_to_sections(
        normalized["sections"],
        current_params,
    )

    context = {
        "route_prefix": route_prefix,
        "product_title": product_title,
        "product_id": product_id,
        "app_title": resolve_localized_text(
            ui_config.app_title, locale, ui_config.locale.default
        ),
        "logo_text": resolve_localized_text(
            ui_config.logo_text, locale, ui_config.locale.default
        ),
        "locale": locale,
        "available_locales": list(ui_config.locale.available),
        "locale_cfg": ui_config.locale,
        "theme": theme,
        "layout": layout,
        "components": build_components_context(ui_config.components),
        "navigation": build_navigation(
            route_prefix=route_prefix,
            navigation=ui_config.navigation,
            active_path="",
            locale=locale,
            default_locale=ui_config.locale.default,
        ),
        "shell_classes": shell_classes,
        "language_switcher": _build_language_switcher(
            request, ui_config.locale, route_prefix
        ),
        "page_title": normalized["title"],
        "page_subtitle": normalized["subtitle"],
        "back_href": back_href,
        "warnings": normalized["warnings"],
        "sections": sections,
        "has_sections": bool(sections),
        "has_warnings": bool(normalized["warnings"]),
        "error": None,
        "status": "ok",
    }

    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context=context,
        status_code=200,
    )
