from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from beeui_module.pages.links import add_preserved_params_to_href
from beeui_module.pages.locale import resolve_localized_text
from beeui_module.pages.models import BeeUiConfig
from beeui_module.pages.router import (
    _build_language_switcher,
    build_layout_context,
    build_navigation,
    build_shell_classes,
    build_theme_context,
    prefixed_path,
    resolve_locale,
)

_CATALOG_SECTION_ORDER = ["interface", "forms", "layout", "extra", "plugins"]


# Разрешение активного таба в демонстрационных примерах каталога компонентов через ?tab= с fallback на default и безопасной проверкой allowlist
def _resolve_url_tab(
    request: Request,
    tabs: list[dict[str, str]],
    *,
    default: str,
) -> str:
    allowed_ids = {
        item["id"] for item in tabs if isinstance(item.get("id"), str) and item["id"]
    }
    candidate = request.query_params.get("tab")
    if candidate in allowed_ids:
        return candidate
    if default in allowed_ids:
        return default
    return next(iter(allowed_ids), "")


def _catalog_sections_for_locale(
    route_prefix: str,
    locale: str,
    default_locale: str,
) -> dict[str, dict[str, str]]:
    sections = _catalog_sections(route_prefix)
    if locale == default_locale:
        return sections

    for section in sections.values():
        section["href"] = add_preserved_params_to_href(
            section["href"],
            {"lang": locale},
            frozenset({"lang"}),
        )
    return sections


# Регистрация маршрутов для компонентного каталога и их рендеринг
def register_component_catalog_routes(
    *,
    app: FastAPI,
    templates: Jinja2Templates,
    route_prefix: str,
    ui_config: BeeUiConfig,
    product_title: str,
    product_id: str,
) -> list[str]:
    registered_routes: list[str] = []

    theme = build_theme_context(ui_config)
    layout = build_layout_context(ui_config)
    shell_classes = build_shell_classes(theme, layout)
    sections = _catalog_sections(route_prefix)

    index_route = prefixed_path(route_prefix, "/components")
    registered_routes.append(index_route)

    async def render_catalog_index(request: Request) -> HTMLResponse:
        locale = resolve_locale(request, ui_config.locale)
        catalog_sections = _catalog_sections_for_locale(
            route_prefix,
            locale,
            ui_config.locale.default,
        )
        samples = _catalog_samples(route_prefix)
        samples["active_url_tab"] = _resolve_url_tab(
            request,
            samples["tabs"],
            default="details",
        )
        return templates.TemplateResponse(
            request=request,
            name="components/catalog/index.html",
            context={
                "route_prefix": route_prefix,
                "product_title": product_title,
                "product_id": product_id,
                "app_title": resolve_localized_text(
                    ui_config.app_title, locale, ui_config.locale.default
                ),
                "logo_text": resolve_localized_text(
                    ui_config.logo_text, locale, ui_config.locale.default
                ),
                "available_locales": list(ui_config.locale.available),
                "locale_cfg": ui_config.locale,
                "language_switcher": _build_language_switcher(
                    request, ui_config.locale, route_prefix
                ),
                "locale": locale,
                "theme": theme,
                "layout": layout,
                "page": {
                    "title": "Component Catalog",
                    "subtitle": "Internal read-only Tabler-compatible primitives",
                },
                "page_title": "Component Catalog",
                "page_subtitle": "Internal read-only Tabler-compatible primitives",
                "navigation": _catalog_navigation(
                    route_prefix=route_prefix,
                    ui_config=ui_config,
                    active_path="/components",
                    locale=locale,
                    default_locale=ui_config.locale.default,
                ),
                "shell_classes": shell_classes,
                "catalog_sections": catalog_sections,
                "samples": samples,
            },
        )

    app.add_api_route(
        index_route,
        render_catalog_index,
        methods=["GET"],
        response_class=HTMLResponse,
    )

    for section_key in _CATALOG_SECTION_ORDER:
        section = sections[section_key]
        route_path = prefixed_path(route_prefix, section["path"])
        registered_routes.append(route_path)

        async def render_catalog_section(
            request: Request, _section: dict[str, str] = section
        ) -> HTMLResponse:
            locale = resolve_locale(request, ui_config.locale)
            catalog_sections = _catalog_sections_for_locale(
                route_prefix,
                locale,
                ui_config.locale.default,
            )
            catalog_section = catalog_sections[_section["id"]]
            samples = _catalog_samples(route_prefix)
            samples["active_url_tab"] = _resolve_url_tab(
                request,
                samples["tabs"],
                default="details",
            )
            return templates.TemplateResponse(
                request=request,
                name="components/catalog/page.html",
                context={
                    "route_prefix": route_prefix,
                    "product_title": product_title,
                    "product_id": product_id,
                    "app_title": resolve_localized_text(
                        ui_config.app_title, locale, ui_config.locale.default
                    ),
                    "logo_text": resolve_localized_text(
                        ui_config.logo_text, locale, ui_config.locale.default
                    ),
                    "available_locales": list(ui_config.locale.available),
                    "locale_cfg": ui_config.locale,
                    "language_switcher": _build_language_switcher(
                        request, ui_config.locale, route_prefix
                    ),
                    "locale": locale,
                    "theme": theme,
                    "layout": layout,
                    "page": {
                        "title": _section["title"],
                        "subtitle": _section["description"],
                    },
                    "page_title": _section["title"],
                    "page_subtitle": _section["description"],
                    "navigation": _catalog_navigation(
                        route_prefix=route_prefix,
                        ui_config=ui_config,
                        active_path=_section["path"],
                        locale=locale,
                        default_locale=ui_config.locale.default,
                    ),
                    "shell_classes": shell_classes,
                    "catalog_sections": catalog_sections,
                    "catalog_section": catalog_section,
                    "samples": samples,
                },
            )

        app.add_api_route(
            route_path,
            render_catalog_section,
            methods=["GET"],
            response_class=HTMLResponse,
        )

    return registered_routes


# Определение структуры разделов каталога компонентов и их метаданных
def _catalog_sections(route_prefix: str) -> dict[str, dict[str, str]]:
    return {
        "interface": {
            "id": "interface",
            "title": "Interface Primitives",
            "path": "/components/interface",
            "href": prefixed_path(route_prefix, "/components/interface"),
            "description": "Alerts, badges, buttons, tabs and basic component shell.",
            "template_name": "components/catalog/sections/interface.html",
        },
        "forms": {
            "id": "forms",
            "title": "Forms Primitives",
            "path": "/components/forms",
            "href": prefixed_path(route_prefix, "/components/forms"),
            "description": "Controlled read-only form primitives for future form surfaces.",
            "template_name": "components/catalog/sections/forms.html",
        },
        "layout": {
            "id": "layout",
            "title": "Layout Primitives",
            "path": "/components/layout",
            "href": prefixed_path(route_prefix, "/components/layout"),
            "description": "Cards, headers, breadcrumb and pagination in a shared style.",
            "template_name": "components/catalog/sections/layout.html",
        },
        "extra": {
            "id": "extra",
            "title": "Extra Primitives",
            "path": "/components/extra",
            "href": prefixed_path(route_prefix, "/components/extra"),
            "description": "Modal, offcanvas, toast and avatar placeholders.",
            "template_name": "components/catalog/sections/extra.html",
        },
        "plugins": {
            "id": "plugins",
            "title": "Plugin Placeholders",
            "path": "/components/plugins",
            "href": prefixed_path(route_prefix, "/components/plugins"),
            "description": "Inert containers for charts, maps and datatables integrations.",
            "template_name": "components/catalog/sections/plugins.html",
        },
    }


# Билд навигационного дерева для каталога компонентов, включая активные состояния
def _catalog_navigation(
    *,
    route_prefix: str,
    ui_config: BeeUiConfig,
    active_path: str,
    locale: str = "en",
    default_locale: str = "en",
) -> list[dict[str, Any]]:
    navigation = build_navigation(
        route_prefix=route_prefix,
        navigation=ui_config.navigation,
        active_path=active_path,
        locale=locale,
        default_locale=default_locale,
    )
    sections = _catalog_sections_for_locale(route_prefix, locale, default_locale)
    catalog_index_href = prefixed_path(route_prefix, "/components")
    if locale != default_locale:
        catalog_index_href = add_preserved_params_to_href(
            catalog_index_href,
            {"lang": locale},
            frozenset({"lang"}),
        )
    navigation.append(
        {
            "title": "Components",
            "path": None,
            "href": None,
            "icon": "components",
            "active": False,
            "descendant_active": active_path.startswith("/components"),
            "disabled": False,
            "children": [
                {
                    "title": "Catalog index",
                    "path": "/components",
                    "href": catalog_index_href,
                    "icon": None,
                    "active": active_path == "/components",
                    "descendant_active": False,
                    "disabled": False,
                    "children": [],
                    "is_group": False,
                },
                {
                    "title": sections["interface"]["title"],
                    "path": sections["interface"]["path"],
                    "href": sections["interface"]["href"],
                    "icon": None,
                    "active": active_path == sections["interface"]["path"],
                    "descendant_active": False,
                    "disabled": False,
                    "children": [],
                    "is_group": False,
                },
                {
                    "title": sections["forms"]["title"],
                    "path": sections["forms"]["path"],
                    "href": sections["forms"]["href"],
                    "icon": None,
                    "active": active_path == sections["forms"]["path"],
                    "descendant_active": False,
                    "disabled": False,
                    "children": [],
                    "is_group": False,
                },
                {
                    "title": sections["layout"]["title"],
                    "path": sections["layout"]["path"],
                    "href": sections["layout"]["href"],
                    "icon": None,
                    "active": active_path == sections["layout"]["path"],
                    "descendant_active": False,
                    "disabled": False,
                    "children": [],
                    "is_group": False,
                },
                {
                    "title": sections["extra"]["title"],
                    "path": sections["extra"]["path"],
                    "href": sections["extra"]["href"],
                    "icon": None,
                    "active": active_path == sections["extra"]["path"],
                    "descendant_active": False,
                    "disabled": False,
                    "children": [],
                    "is_group": False,
                },
                {
                    "title": sections["plugins"]["title"],
                    "path": sections["plugins"]["path"],
                    "href": sections["plugins"]["href"],
                    "icon": None,
                    "active": active_path == sections["plugins"]["path"],
                    "descendant_active": False,
                    "disabled": False,
                    "children": [],
                    "is_group": False,
                },
            ],
            "is_group": True,
        }
    )
    return navigation


# Пример данных для демонстрации различных компонентов в каталоге, включая небезопасные строки для проверки экранирования
def _catalog_samples(route_prefix: str) -> dict[str, Any]:
    return {
        "unsafe_text": "<script>alert(6)</script>",
        "unsafe_input": '<img src=x onerror="alert(2)">',
        "status": "degraded",
        "status_label": "Read-only preview",
        "alert_title": "Escaping sample",
        "alert_message": 'Unsafe sample string: <svg onload="alert(1)"></svg>',
        "table_columns": ["Name", "Value", "Status"],
        "table_rows": [
            ["alpha", "42", "ok"],
            ["beta", "17", "warning"],
            ["gamma", "5", "error"],
        ],
        "grid_columns": ["ID", "Owner", "Stage"],
        "grid_rows": [
            {"ID": "run_001", "Owner": "demo", "Stage": "queued"},
            {"ID": "run_002", "Owner": "demo", "Stage": "ready"},
        ],
        "select_options": ["Alpha", "Beta", "Gamma"],
        "interface_url": prefixed_path(route_prefix, "/components/interface"),
        "tabs": [
            {"id": "overview", "title": "Overview"},
            {"id": "details", "title": "Details"},
            {"id": "history", "title": "History"},
        ],
        "breadcrumbs": [
            {"title": "Home", "href": prefixed_path(route_prefix, "/")},
            {
                "title": "Components",
                "href": prefixed_path(route_prefix, "/components"),
            },
            {"title": "Catalog", "href": None},
        ],
    }
