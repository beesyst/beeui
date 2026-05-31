from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from beeui_module.pages.models import BeeUiConfig, BeeUiNavigationItem, BeeUiPage


# Регистрация маршрутов для страниц BeeUI в FastAPI приложении
def register_configured_pages(
    *,
    app: FastAPI,
    templates: Jinja2Templates,
    route_prefix: str,
    ui_config: BeeUiConfig,
    product_title: str,
    product_id: str,
) -> list[str]:
    registered_routes: list[str] = []

    for page in ui_config.pages:
        route_path = prefixed_path(route_prefix, page.path)
        registered_routes.append(route_path)

        async def render_page(
            request: Request, _page: BeeUiPage = page
        ) -> HTMLResponse:
            return templates.TemplateResponse(
                request=request,
                name="page.html",
                context={
                    "route_prefix": route_prefix,
                    "product_title": product_title,
                    "product_id": product_id,
                    "app_title": ui_config.app_title,
                    "page": _page,
                    "navigation": build_navigation(
                        route_prefix=route_prefix,
                        navigation=ui_config.navigation,
                        active_path=_page.path,
                    ),
                    "has_blocks": bool(_page.blocks),
                },
            )

        app.add_api_route(
            route_path, render_page, methods=["GET"], response_class=HTMLResponse
        )

    return registered_routes


# Билд навигационных элементов с учетом активного пути
def build_navigation(
    *,
    route_prefix: str,
    navigation: list[BeeUiNavigationItem],
    active_path: str,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in navigation:
        items.append(
            {
                "title": item.title,
                "path": item.path,
                "href": prefixed_path(route_prefix, item.path),
                "icon": item.icon,
                "active": item.path == active_path,
            }
        )
    return items


# Корректное формирование пути с учетом префикса маршрута
def prefixed_path(route_prefix: str, path: str) -> str:
    if path == "/":
        return route_prefix or "/"
    if route_prefix:
        return f"{route_prefix}{path}"
    return path
