from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit, urlunsplit

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from beeui_module.artifacts.redaction import redact_value
from beeui_module.blocks.layout_renderer import layout_has_charts, render_layout
from beeui_module.blocks.registry import resolve_page_blocks
from beeui_module.pages.config import is_custom_route_reserved_path
from beeui_module.pages.models import (
    BeeUiConfig,
    BeeUiNavigationItem,
    BeeUiPage,
    ComponentConfig,
    LocaleConfig,
)

TABS_VARIANT_CLASSES: dict[str, str] = {
    "default": "nav nav-tabs card-header-tabs",
    "reverse": "nav nav-tabs card-header-tabs flex-row-reverse",
    "fill": "nav nav-tabs card-header-tabs nav-fill",
    "icons": "nav nav-tabs card-header-tabs",
    "fill_icons": "nav nav-tabs card-header-tabs nav-fill",
    "dropdown": "nav nav-tabs card-header-tabs",
}
ACCORDION_VARIANT_CLASSES: dict[str, str] = {
    "default": "accordion",
    "flush": "accordion accordion-flush",
    "tabs": "accordion accordion-tabs",
    "inverted": "accordion accordion-inverted",
    "inverted_plus": "accordion accordion-inverted accordion-plus",
    "icons": "accordion",
}
RESERVED_CUSTOM_PAGE_PATHS: frozenset[str] = frozenset(
    {
        "/",
        "/health",
        "/static",
        "/api",
        "/auth",
        "/components",
        "/login",
        "/logout",
    }
)


# Разрешение локали: default из config, ?lang= override если allowlist содержит
def resolve_locale(
    request: Request,
    locale_cfg: LocaleConfig,
) -> str:
    lang = request.query_params.get("lang")
    if lang and lang in locale_cfg.available:
        return lang
    return locale_cfg.default


# Регистрация HTML routes из declarative pages config
def register_configured_pages(
    *,
    app: FastAPI,
    templates: Jinja2Templates,
    route_prefix: str,
    ui_config: BeeUiConfig,
    product_title: str,
    product_id: str,
    route_modes: dict[str, str] | None = None,
    excluded_paths: set[str] | None = None,
) -> list[str]:
    registered_routes: list[str] = []
    skipped_paths = excluded_paths or set()

    for page in ui_config.pages:
        if route_modes is not None and route_modes.get(page.path) != "configured":
            continue
        if is_custom_route_reserved_path(page.path):
            continue
        if page.path in skipped_paths:
            continue
        route_path = prefixed_path(route_prefix, page.path)
        registered_routes.append(route_path)

        async def render_page(
            request: Request, _page: BeeUiPage = page
        ) -> HTMLResponse:
            theme = build_theme_context(ui_config)
            layout = build_layout_context(ui_config)
            rendered_blocks = resolve_page_blocks(
                placements=_page.blocks,
                registry=ui_config.blocks,
                data_sources=ui_config.data_sources,
            )
            locale = resolve_locale(request, ui_config.locale)
            page_tabs_data = _resolve_page_tabs_data(
                _page,
                request,
                route_prefix=route_prefix,
            )

            has_charts = any(
                getattr(b, "block_type", None) == "chart" for b in rendered_blocks
            )

            return templates.TemplateResponse(
                request=request,
                name="page.html",
                context={
                    "route_prefix": route_prefix,
                    "product_title": product_title,
                    "product_id": product_id,
                    "app_title": ui_config.app_title,
                    "logo_text": ui_config.logo_text,
                    "locale": locale,
                    "theme": theme,
                    "layout": layout,
                    "page": _page,
                    "components": build_components_context(ui_config.components),
                    "page_tabs": page_tabs_data,
                    "navigation": build_navigation(
                        route_prefix=route_prefix,
                        navigation=ui_config.navigation,
                        active_path=_page.path,
                    ),
                    "shell_classes": build_shell_classes(theme, layout),
                    "rendered_blocks": rendered_blocks,
                    "has_blocks": bool(rendered_blocks),
                    "has_layout": False,
                    "layout_blocks": [],
                    "has_charts": has_charts,
                    "error": None,
                    "status": "ok",
                },
            )

        app.add_api_route(
            route_path, render_page, methods=["GET"], response_class=HTMLResponse
        )

    return registered_routes


# Билд navigation context с active/descendant_active состояниями
def build_navigation(
    *,
    route_prefix: str,
    navigation: list[BeeUiNavigationItem],
    active_path: str,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in navigation:
        children = build_navigation(
            route_prefix=route_prefix,
            navigation=item.children,
            active_path=active_path,
        )
        active = item.path == active_path if item.path is not None else False
        descendant_active = any(
            child["active"] or child["descendant_active"] for child in children
        )
        items.append(
            {
                "title": item.title,
                "path": item.path,
                "href": prefixed_path(route_prefix, item.path)
                if item.path and not item.disabled
                else None,
                "icon": item.icon,
                "active": active,
                "descendant_active": descendant_active,
                "disabled": item.disabled,
                "children": children,
                "is_group": bool(item.children),
            }
        )
    return items


# Преобразование ThemeConfig в безопасные CSS class names для shell
def build_theme_context(ui_config: BeeUiConfig) -> dict[str, Any]:
    return {
        "mode": ui_config.theme.mode,
        "primary": ui_config.theme.primary,
        "base": ui_config.theme.base,
        "font": ui_config.theme.font,
        "radius": ui_config.theme.radius,
        "density": ui_config.theme.density,
        "mode_class": f"beeui-theme-mode-{ui_config.theme.mode}",
        "primary_class": f"beeui-theme-primary-{ui_config.theme.primary}",
        "base_class": f"beeui-theme-base-{ui_config.theme.base}",
        "font_class": f"beeui-theme-font-{ui_config.theme.font}",
        "radius_class": f"beeui-radius-{ui_config.theme.radius}",
        "density_class": f"beeui-density-{ui_config.theme.density}",
    }


# Преобразование LayoutConfig в template context для контейнера, sidebar и navbar
def build_layout_context(ui_config: BeeUiConfig) -> dict[str, Any]:
    layout = ui_config.layout
    return {
        "type": layout.type,
        "container": layout.container,
        "container_class": "container-fluid"
        if layout.container == "fluid"
        else "container-xl",
        "type_class": f"beeui-layout-{layout.type}",
        "sidebar_variant": layout.sidebar.variant,
        "sidebar_variant_class": f"beeui-sidebar-variant-{layout.sidebar.variant}",
        "sidebar_collapsed": layout.sidebar.collapsed,
        "sidebar_collapsed_class": "beeui-sidebar-collapsed"
        if layout.sidebar.collapsed
        else "",
        "navbar_enabled": layout.navbar.enabled,
        "navbar_variant": layout.navbar.variant,
        "navbar_variant_class": f"beeui-navbar-variant-{layout.navbar.variant}",
        "navbar_sticky": layout.navbar.sticky,
        "navbar_sticky_class": "beeui-navbar-sticky" if layout.navbar.sticky else "",
    }


# Сбор итогового набора CSS classes для body/page shell
def build_shell_classes(theme: dict[str, Any], layout: dict[str, Any]) -> str:
    classes = [
        "layout-vertical",
        layout["type_class"],
        layout["sidebar_variant_class"],
        layout["sidebar_collapsed_class"],
        theme["mode_class"],
        theme["primary_class"],
        theme["base_class"],
        theme["font_class"],
        theme["radius_class"],
        theme["density_class"],
    ]
    if layout["navbar_enabled"]:
        classes.extend(
            [
                layout["navbar_variant_class"],
                layout["navbar_sticky_class"],
            ]
        )
    return " ".join(class_name for class_name in classes if class_name)


# Префиксация внутренних tab href с учетом route_prefix BeeUI
def _prefix_internal_href(route_prefix: str, href: str) -> str:
    parsed = urlsplit(href)
    prefixed_path_value = prefixed_path(route_prefix, parsed.path)
    return urlunsplit(("", "", prefixed_path_value, parsed.query, ""))


# Сбор безопасного контекста для URL-driven tabs на странице
def _resolve_page_tabs_data(
    page: BeeUiPage,
    request: Request,
    *,
    route_prefix: str,
) -> dict[str, Any] | None:
    if page.tabs is None or not page.tabs.items:
        return None

    items_list = []
    for item in page.tabs.items:
        items_list.append(
            {
                "id": item.tab_id,
                "title": item.title,
                "href": _prefix_internal_href(route_prefix, item.href),
                "disabled": item.disabled,
            }
        )
    enabled_items = [item for item in page.tabs.items if not item.disabled]
    requested_active_id = request.query_params.get(page.tabs.active_param)
    enabled_item_ids = {item.tab_id for item in enabled_items}
    active_id = (
        requested_active_id
        if requested_active_id in enabled_item_ids
        else (enabled_items[0].tab_id if enabled_items else page.tabs.items[0].tab_id)
    )
    return {
        "tab_items": items_list,
        "active_id": active_id,
        "tabs_class": tabs_class_for_variant(page.tabs.variant),
        "active_param": page.tabs.active_param,
    }


# Разрешение CSS-классов tabs из валидированного variant
def tabs_class_for_variant(variant: str) -> str:
    return TABS_VARIANT_CLASSES.get(variant, TABS_VARIANT_CLASSES["default"])


# Разрешение CSS-классов accordion из валидированного variant
def accordion_class_for_variant(variant: str) -> str:
    return ACCORDION_VARIANT_CLASSES.get(
        variant,
        ACCORDION_VARIANT_CLASSES["default"],
    )


# Сбор component context для Jinja templates
def build_components_context(components: ComponentConfig) -> dict[str, Any]:
    tabs_variant = components.tabs.variant
    accordion_variant = components.accordion.variant
    return {
        "tabs_variant": tabs_variant,
        "tabs_class": tabs_class_for_variant(tabs_variant),
        "accordion_variant": accordion_variant,
        "accordion_class": accordion_class_for_variant(accordion_variant),
        "tabs_variants": TABS_VARIANT_CLASSES,
        "accordion_variants": ACCORDION_VARIANT_CLASSES,
    }


# Регистрация маршрутов только для запросов GET для пользовательских страниц, поддерживаемых адаптером и объявленных в конфигурации
def register_adapter_custom_pages(
    *,
    app: FastAPI,
    templates: Jinja2Templates,
    route_prefix: str,
    ui_config: BeeUiConfig,
    product_title: str,
    product_id: str,
    route_modes: dict[str, str] | None = None,
    excluded_paths: set[str] | None = None,
) -> list[str]:
    registered_routes: list[str] = []
    skipped_paths = excluded_paths or set()

    theme = build_theme_context(ui_config)
    layout = build_layout_context(ui_config)
    shell_classes = build_shell_classes(theme, layout)

    for page in ui_config.pages:
        if route_modes is not None and route_modes.get(page.path) != "adapter":
            continue
        if page.path in skipped_paths:
            continue
        if page.path in RESERVED_CUSTOM_PAGE_PATHS:
            continue
        if is_custom_route_reserved_path(page.path):
            continue
        route_path = prefixed_path(route_prefix, page.path)
        registered_routes.append(route_path)

        async def render_adapter_page(
            request: Request, _page: BeeUiPage = page
        ) -> HTMLResponse:
            adapter = getattr(request.app.state, "beeui_adapter", None)
            if adapter is None:
                return _render_page_unavailable(
                    request,
                    templates,
                    route_prefix,
                    ui_config,
                    product_title,
                    product_id,
                    _page,
                    error="Adapter is not available",
                    status_code=503,
                )

            method = getattr(adapter, "get_page", None)
            if not callable(method):
                return _render_page_unavailable(
                    request,
                    templates,
                    route_prefix,
                    ui_config,
                    product_title,
                    product_id,
                    _page,
                    error=f"Page {_page.page_id} is unavailable",
                    status_code=503,
                )

            try:
                query = dict(request.query_params)
                result = method(_page.page_id, query)
            except Exception:
                return _render_page_unavailable(
                    request,
                    templates,
                    route_prefix,
                    ui_config,
                    product_title,
                    product_id,
                    _page,
                    error=f"Failed to load page {_page.page_id}",
                    status_code=502,
                )

            from beeui_module.adapters.envelopes import (
                AdapterErrorResult,
                AdapterResult,
            )

            if isinstance(result, AdapterErrorResult):
                return _render_page_unavailable(
                    request,
                    templates,
                    route_prefix,
                    ui_config,
                    product_title,
                    product_id,
                    _page,
                    error=str(
                        redact_value(result.error.get("message", "Page unavailable"))
                    ),
                    status_code=503,
                )

            if not isinstance(result, AdapterResult) or not isinstance(
                result.data, dict
            ):
                return _render_page_unavailable(
                    request,
                    templates,
                    route_prefix,
                    ui_config,
                    product_title,
                    product_id,
                    _page,
                    error=f"Adapter returned malformed payload for page {_page.page_id}",
                    status_code=502,
                )

            payload = redact_value(result.data)
            if not isinstance(payload, dict):
                return _render_page_unavailable(
                    request,
                    templates,
                    route_prefix,
                    ui_config,
                    product_title,
                    product_id,
                    _page,
                    error=f"Adapter returned malformed payload for page {_page.page_id}",
                    status_code=502,
                )

            layout_blocks = render_layout(payload.get("layout"))
            has_layout = bool(layout_blocks)

            locale = resolve_locale(request, ui_config.locale)
            page_tabs_data = _resolve_page_tabs_data(
                _page,
                request,
                route_prefix=route_prefix,
            )

            has_charts = layout_has_charts(layout_blocks)

            context = {
                "route_prefix": route_prefix,
                "product_title": product_title,
                "product_id": product_id,
                "app_title": ui_config.app_title,
                "logo_text": ui_config.logo_text,
                "locale": locale,
                "theme": theme,
                "layout": layout,
                "page": _page,
                "components": build_components_context(ui_config.components),
                "page_tabs": page_tabs_data,
                "navigation": build_navigation(
                    route_prefix=route_prefix,
                    navigation=ui_config.navigation,
                    active_path=_page.path,
                ),
                "shell_classes": shell_classes,
                "has_layout": has_layout,
                "layout_blocks": layout_blocks,
                "has_charts": has_charts,
                "has_blocks": False,
                "rendered_blocks": [],
                "page_title": _page.title,
                "page_subtitle": _page.subtitle,
                "error": None,
                "warnings": [],
                "meta": {},
                "status": "ok",
            }
            return templates.TemplateResponse(
                request=request,
                name="page.html",
                context=context,
                status_code=200,
            )

        app.add_api_route(
            route_path,
            render_adapter_page,
            methods=["GET"],
            response_class=HTMLResponse,
        )

    return registered_routes


# Рендер degraded-state для adapter-backed custom page
def _render_page_unavailable(
    request: Request,
    templates: Jinja2Templates,
    route_prefix: str,
    ui_config: BeeUiConfig,
    product_title: str,
    product_id: str,
    page: BeeUiPage,
    *,
    error: str,
    status_code: int = 503,
) -> HTMLResponse:
    theme = build_theme_context(ui_config)
    layout = build_layout_context(ui_config)
    locale = resolve_locale(request, ui_config.locale)
    page_tabs_data = _resolve_page_tabs_data(
        page,
        request,
        route_prefix=route_prefix,
    )
    context = {
        "route_prefix": route_prefix,
        "product_title": product_title,
        "product_id": product_id,
        "app_title": ui_config.app_title,
        "logo_text": ui_config.logo_text,
        "locale": locale,
        "theme": theme,
        "layout": layout,
        "page": page,
        "components": build_components_context(ui_config.components),
        "page_tabs": page_tabs_data,
        "navigation": build_navigation(
            route_prefix=route_prefix,
            navigation=ui_config.navigation,
            active_path=page.path,
        ),
        "shell_classes": build_shell_classes(theme, layout),
        "has_layout": False,
        "layout_blocks": [],
        "has_charts": False,
        "has_blocks": False,
        "rendered_blocks": [],
        "page_title": page.title,
        "page_subtitle": page.subtitle,
        "error": error,
        "warnings": [],
        "meta": {},
        "status": "unavailable",
    }
    return templates.TemplateResponse(
        request=request,
        name="page.html",
        context=context,
        status_code=status_code,
    )


# Добавление route_prefix без изменения корневого пути
def prefixed_path(route_prefix: str, path: str) -> str:
    if path == "/":
        return route_prefix or "/"
    if route_prefix:
        return f"{route_prefix}{path}"
    return path
