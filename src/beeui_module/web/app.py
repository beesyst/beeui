from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from beeui_module.adapters.base import ProductUiAdapter
from beeui_module.adapters.envelopes import AdapterMetadata
from beeui_module.artifacts.routes import register_artifact_routes
from beeui_module.core.paths import schema_path, settings_path
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version
from beeui_module.pages.component_catalog import register_component_catalog_routes
from beeui_module.pages.config import load_beeui_config
from beeui_module.pages.models import BeeUiConfig
from beeui_module.pages.product_console import register_product_console_routes
from beeui_module.pages.router import register_configured_pages


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


# Валидация mount path для mount_beeui
def _validate_mount_path(path: str) -> str:
    if not path:
        raise ValueError("Mount path must be a non-empty string")
    if not path.startswith("/"):
        raise ValueError("Mount path must start with '/'")
    if path == "/":
        raise ValueError("Mount path must not be '/' (use create_beeui_app directly)")
    if ".." in path.split("/"):
        raise ValueError("Mount path must not contain '..'")
    if "//" in path:
        raise ValueError("Mount path must not contain '//'")
    if "?" in path or "#" in path or "&" in path:
        raise ValueError("Mount path must not contain query or fragment characters")
    # Normalize: remove trailing slash
    normalized = path.rstrip("/")
    if normalized != path:
        raise ValueError("Mount path must not have trailing slash")
    return normalized


# Runtime-проверка, что переданный adapter соответствует минимальному протоколу ProductUiAdapter
def _validate_adapter(adapter: Any) -> None:
    if not hasattr(adapter, "metadata"):
        raise ValueError(
            "Adapter must have a 'metadata' attribute of type AdapterMetadata"
        )
    if not isinstance(adapter.metadata, AdapterMetadata):
        raise ValueError("Adapter.metadata must be an instance of AdapterMetadata")
    required_read_methods = [
        "get_dashboard",
        "list_runs",
        "get_run",
        "list_artifacts",
        "read_artifact",
        "get_config_read_model",
    ]
    for method_name in required_read_methods:
        if not hasattr(adapter, method_name):
            raise ValueError(f"Adapter must have method '{method_name}'")
        method = getattr(adapter, method_name)
        if not callable(method):
            raise ValueError(f"Adapter.{method_name} must be callable")


# Получение product metadata из adapter или переданных параметров
def _resolve_product_metadata(
    product_id: str | None,
    product_title: str | None,
    adapter: ProductUiAdapter | None,
    settings_product: dict[str, Any],
) -> dict[str, Any]:
    pid = product_id or settings_product["id"]
    ptitle = product_title or settings_product["title"]

    result: dict[str, Any] = {"id": pid, "title": ptitle}

    if adapter is not None:
        meta = adapter.metadata
        result["product_id"] = meta.product_id
        result["product_title"] = meta.title
        result["adapter_version"] = meta.version
        if meta.capabilities:
            result["capabilities"] = list(meta.capabilities)

    return result


# Выбор source of truth для UI config
def _resolve_ui_config(
    ui_config: BeeUiConfig | None,
    config_path: Path | str | None,
) -> BeeUiConfig:
    if ui_config is not None:
        return ui_config
    if config_path is not None:
        return load_beeui_config(Path(config_path))
    return load_beeui_config(schema_path())


# Создание экземпляра FastAPI с учетом настроек и маршрутов
def create_beeui_app(
    settings: dict[str, Any] | None = None,
    ui_config: BeeUiConfig | None = None,
    *,
    config_path: str | Path | None = None,
    product_id: str | None = None,
    product_title: str | None = None,
    adapter: ProductUiAdapter | None = None,
) -> FastAPI:
    if adapter is not None:
        _validate_adapter(adapter)

    resolved_settings = (
        settings if settings is not None else load_settings(settings_path())
    )
    resolved_ui_config = _resolve_ui_config(ui_config, config_path)
    web_cfg = resolved_settings["web"]
    security_cfg = resolved_settings["security"]
    product_cfg = resolved_settings["product"]
    features_cfg = resolved_settings["features"]

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

    product_meta = _resolve_product_metadata(
        product_id=product_id,
        product_title=product_title,
        adapter=adapter,
        settings_product=product_cfg,
    )

    app.state.beeui_adapter = adapter
    app.state.beeui_product = product_meta

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

    health_path = f"{route_prefix}/health" if route_prefix else "/health"

    excluded_paths: set[str] = set()
    if adapter is not None:
        register_product_console_routes(
            app=app,
            templates=templates,
            route_prefix=route_prefix,
            ui_config=resolved_ui_config,
            product_title=product_meta["title"],
            product_id=product_meta["id"],
        )
        excluded_paths = {"/", "/runs"}

    register_configured_pages(
        app=app,
        templates=templates,
        route_prefix=route_prefix,
        ui_config=resolved_ui_config,
        product_title=product_meta["title"],
        product_id=product_meta["id"],
        excluded_paths=excluded_paths,
    )

    register_component_catalog_routes(
        app=app,
        templates=templates,
        route_prefix=route_prefix,
        ui_config=resolved_ui_config,
        product_title=product_meta["title"],
        product_id=product_meta["id"],
    )

    if features_cfg["browser_artifact"]:
        register_artifact_routes(
            app=app,
            templates=templates,
            route_prefix=route_prefix,
            ui_config=resolved_ui_config,
            product_title=product_meta["title"],
            product_id=product_meta["id"],
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


# Хелпер: встраивание BeeUI в родительское FastAPI приложение
def mount_beeui(
    app: FastAPI,
    *,
    path: str = "/ui",
    settings: dict[str, Any] | None = None,
    ui_config: BeeUiConfig | None = None,
    config_path: str | Path | None = None,
    product_id: str | None = None,
    product_title: str | None = None,
    adapter: ProductUiAdapter | None = None,
) -> FastAPI:
    safe_path = _validate_mount_path(path)
    _check_route_collision(app, safe_path)

    child_app = create_beeui_app(
        settings=settings,
        ui_config=ui_config,
        config_path=config_path,
        product_id=product_id,
        product_title=product_title,
        adapter=adapter,
    )

    app.mount(
        safe_path, child_app, name=f"beeui_{safe_path.lstrip('/').replace('/', '_')}"
    )

    return app


# Чек на коллизию маршрутов в родительском приложении
def _check_route_collision(app: FastAPI, mount_path: str) -> None:
    for route in app.routes:
        route_path = getattr(route, "path", None)
        if not isinstance(route_path, str):
            continue

        existing = route_path.rstrip("/")
        if existing == mount_path or existing.startswith(f"{mount_path}/"):
            raise ValueError(
                f"Mount path '{mount_path}' conflicts with existing route "
                f"'{route_path}'"
            )
