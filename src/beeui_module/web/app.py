from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version


# Нормализация route_prefix для корректного формирования маршрутов
def _normalize_prefix(route_prefix: str) -> str:
    cleaned = route_prefix.strip()
    if not cleaned:
        return ""
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    return cleaned.rstrip("/")


# Разрешение директории с шаблонами для Jinja2
def _resolve_templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


# Разрешение директории со статикой и проверка ее наличия
def _resolve_static_dir() -> Path:
    static_dir = Path(__file__).resolve().parent / "static"
    if not static_dir.is_dir():
        raise ValueError(f"Static root directory is missing: {static_dir}")
    return static_dir


# Создание экземпляра FastAPI с учетом настроек и маршрутов
def create_beeui_app(settings: dict[str, Any] | None = None) -> FastAPI:
    resolved_settings = (
        settings if settings is not None else load_settings(settings_path())
    )
    web_cfg = resolved_settings["web"]
    security_cfg = resolved_settings["security"]
    product_cfg = resolved_settings["product"]

    route_prefix = _normalize_prefix(web_cfg["route_prefix"])
    static_cache_seconds = web_cfg["cache_static"]

    app = FastAPI(title="BeeUI", docs_url=None, redoc_url=None, openapi_url=None)

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = bool(security_cfg["html_autoescape"])

    static_path = f"{route_prefix}/static" if route_prefix else "/static"
    app.mount(
        static_path,
        StaticFiles(directory=_resolve_static_dir()),
        name="static",
    )

    @app.middleware("http")
    async def add_read_only_headers(request: Request, call_next):
        response = await call_next(request)
        if request.method == "GET":
            response.headers["X-BeeUI-Read-Only"] = "true"

            if request.url.path == f"{route_prefix}/health":
                response.headers["Cache-Control"] = "no-store"
            elif request.url.path.startswith(f"{static_path}/"):
                response.headers["Cache-Control"] = (
                    f"public, max-age={static_cache_seconds}"
                )
            elif response.headers.get("content-type", "").startswith("text/html"):
                response.headers["Cache-Control"] = "no-store"

        return response

    index_path = route_prefix or "/"
    health_path = f"{route_prefix}/health" if route_prefix else "/health"

    @app.get(index_path, response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "route_prefix": route_prefix,
                "product_title": product_cfg["title"],
                "product_id": product_cfg["id"],
            },
        )

    @app.get(health_path, response_class=JSONResponse)
    async def health() -> JSONResponse:
        return JSONResponse(
            {
                "status": "ok",
                "app": "beeui",
                "version": get_version(),
                "read_only": True,
            }
        )

    return app
