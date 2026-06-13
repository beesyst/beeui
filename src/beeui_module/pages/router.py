from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from beeui_module.blocks.registry import resolve_page_blocks
from beeui_module.pages.models import (
    BeeUiConfig,
    BeeUiNavigationItem,
    BeeUiPage,
    LocaleConfig,
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
    excluded_paths: set[str] | None = None,
) -> list[str]:
    registered_routes: list[str] = []
    skipped_paths = excluded_paths or set()

    for page in ui_config.pages:
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
                    "navigation": build_navigation(
                        route_prefix=route_prefix,
                        navigation=ui_config.navigation,
                        active_path=_page.path,
                    ),
                    "shell_classes": build_shell_classes(theme, layout),
                    "rendered_blocks": rendered_blocks,
                    "has_blocks": bool(rendered_blocks),
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


# Добавление route_prefix без изменения корневого пути
def prefixed_path(route_prefix: str, path: str) -> str:
    if path == "/":
        return route_prefix or "/"
    if route_prefix:
        return f"{route_prefix}{path}"
    return path
