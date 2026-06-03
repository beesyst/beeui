from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from beeui_module.adapters.envelopes import (
    AdapterErrorResult,
    AdapterResult,
)
from beeui_module.adapters.ids import validate_artifact_id, validate_run_id
from beeui_module.artifacts.models import ArtifactPreview
from beeui_module.artifacts.preview import build_preview
from beeui_module.pages.models import BeeUiConfig
from beeui_module.pages.router import (
    build_layout_context,
    build_navigation,
    build_shell_classes,
    build_theme_context,
)


# Маршрут артефактов
def _resolve_adapter(request: Request) -> Any | None:
    return getattr(request.app.state, "beeui_adapter", None)


# Унифицированный ответ при отсутствии адаптера
def _adapter_unavailable_response() -> dict[str, Any]:
    return {
        "status": "error",
        "error": {"code": "adapter_unavailable", "message": "Adapter is not available"},
    }


# Нормализация artifact list от adapter: adapter response тоже untrusted input
def _normalize_artifact_items(
    raw_data: Any,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    artifacts: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not isinstance(raw_data, list):
        return artifacts, [
            {
                "code": "malformed_adapter_payload",
                "message": "Adapter returned non-list artifact payload",
            }
        ]

    for item in raw_data:
        if not isinstance(item, dict):
            warnings.append(
                {
                    "code": "malformed_artifact_item",
                    "message": "Artifact item is not an object",
                }
            )
            continue

        artifact_id = item.get("artifact_id")
        if not isinstance(artifact_id, str):
            warnings.append(
                {
                    "code": "invalid_artifact_id",
                    "message": "Adapter returned invalid artifact_id",
                }
            )
            continue

        try:
            validate_artifact_id(artifact_id)
        except Exception:
            warnings.append(
                {
                    "code": "invalid_artifact_id",
                    "message": "Adapter returned invalid artifact_id",
                }
            )
            continue

        artifacts.append(
            {
                "artifact_id": artifact_id,
                "content_type": str(item.get("content_type", "unknown")),
            }
        )

    return artifacts, warnings


# Конвертация результата адаптера в JSON-ответ для списка артефактов
def _artifact_list_to_json(
    adapter_result: AdapterResult | AdapterErrorResult,
) -> dict[str, Any]:
    """Convert adapter list result to JSON response dict."""
    if isinstance(adapter_result, AdapterErrorResult):
        return adapter_result.to_dict()
    d = adapter_result.to_dict()
    artifacts, item_warnings = _normalize_artifact_items(d["data"])
    return {
        "status": d["status"],
        "data": artifacts,
        "warnings": [*d["warnings"], *item_warnings],
        "meta": d["meta"],
    }


# Конвертация результата адаптера + превью в JSON-ответ для детали артефакта
def _artifact_preview_to_json(
    adapter_result: AdapterResult | AdapterErrorResult,
    preview: ArtifactPreview,
) -> dict[str, Any]:
    if isinstance(adapter_result, AdapterErrorResult):
        base = adapter_result.to_dict()
        return base

    d = adapter_result.to_dict()
    return {
        "status": d["status"],
        "data": {
            "artifact_id": preview.artifact_id,
            "content_type": preview.content_type,
            "preview_type": preview.preview_type,
            "preview_data": preview.preview_data,
            "truncated": preview.truncated,
            "row_count": preview.row_count,
            "row_warnings": list(preview.row_warnings) if preview.row_warnings else [],
            "error": preview.error,
            "metadata_only": preview.metadata_only,
        },
        "warnings": d["warnings"],
        "meta": d["meta"],
    }


# Регистрация read-only artifact routes
def _build_page_context(
    ui_config: BeeUiConfig,
    route_prefix: str,
    *,
    product_title: str,
    product_id: str,
) -> dict[str, Any]:
    theme = build_theme_context(ui_config)
    layout = build_layout_context(ui_config)
    navigation = build_navigation(
        route_prefix=route_prefix,
        navigation=ui_config.navigation,
        active_path="",
    )
    shell_classes = build_shell_classes(theme, layout)

    return {
        "route_prefix": route_prefix,
        "app_title": ui_config.app_title,
        "product_title": product_title,
        "product_id": product_id,
        "logo_text": ui_config.logo_text,
        "theme": theme,
        "layout": layout,
        "navigation": navigation,
        "shell_classes": shell_classes,
    }


# Регистрация маршрутов для артефактов (список и детальный просмотр)
def register_artifact_routes(
    app: FastAPI,
    templates: Jinja2Templates,
    route_prefix: str,
    *,
    ui_config: BeeUiConfig | None = None,
    product_title: str = "BeeUI",
    product_id: str = "beeui",
) -> None:
    _base_ctx: dict[str, Any] = {}
    if ui_config is not None:
        _base_ctx = _build_page_context(
            ui_config,
            route_prefix,
            product_title=product_title,
            product_id=product_id,
        )
    else:
        _base_ctx = {
            "route_prefix": route_prefix,
            "app_title": "BeeUI",
            "product_title": "BeeUI",
            "logo_text": "BeeUI",
            "theme": {"mode": "dark"},
            "layout": {
                "type_class": "layout-vertical",
                "container_class": "container-xl",
            },
            "navigation": [],
            "shell_classes": "layout-vertical",
        }
    list_html_path = f"{route_prefix}/runs/{{run_id}}/artifacts"

    @app.get(list_html_path, response_class=HTMLResponse, include_in_schema=False)
    async def artifact_list_html(request: Request, run_id: str) -> HTMLResponse:
        try:
            validate_run_id(run_id)
        except Exception:
            return templates.TemplateResponse(
                request=request,
                name="artifacts/list.html",
                status_code=400,
                context={
                    **_base_ctx,
                    "run_id": run_id,
                    "artifacts": [],
                    "adapter_available": False,
                    "error": f"Invalid run_id: {run_id}",
                },
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            return templates.TemplateResponse(
                request=request,
                name="artifacts/list.html",
                status_code=503,
                context={
                    **_base_ctx,
                    "run_id": run_id,
                    "artifacts": [],
                    "adapter_available": False,
                    "error": "Adapter is not available",
                },
            )

        result = adapter.list_artifacts(run_id)
        error: str | None = None
        artifacts: list[dict[str, Any]] = []

        if isinstance(result, AdapterErrorResult):
            error = result.error.get("message", "Unknown error")
        else:
            raw_data = result.data
            if isinstance(raw_data, list):
                artifacts, _warnings = _normalize_artifact_items(result.data)

        return templates.TemplateResponse(
            request=request,
            name="artifacts/list.html",
            context={
                **_base_ctx,
                "run_id": run_id,
                "artifacts": artifacts,
                "adapter_available": True,
                "error": error,
            },
        )

    detail_html_path = f"{route_prefix}/runs/{{run_id}}/artifacts/{{artifact_id}}"

    @app.get(detail_html_path, response_class=HTMLResponse, include_in_schema=False)
    async def artifact_detail_html(
        request: Request, run_id: str, artifact_id: str
    ) -> HTMLResponse:
        # Validate IDs before passing to adapter
        try:
            validate_run_id(run_id)
            validate_artifact_id(artifact_id)
        except Exception:
            return templates.TemplateResponse(
                request=request,
                name="artifacts/detail.html",
                status_code=400,
                context={
                    **_base_ctx,
                    "run_id": run_id,
                    "artifact_id": artifact_id,
                    "adapter_available": False,
                    "error": "Invalid run_id or artifact_id",
                    "preview": None,
                },
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            return templates.TemplateResponse(
                request=request,
                name="artifacts/detail.html",
                status_code=503,
                context={
                    **_base_ctx,
                    "run_id": run_id,
                    "artifact_id": artifact_id,
                    "adapter_available": False,
                    "error": "Adapter is not available",
                    "preview": None,
                },
            )

        result = adapter.read_artifact(run_id, artifact_id)
        error: str | None = None
        preview: ArtifactPreview | None = None

        if isinstance(result, AdapterErrorResult):
            error = result.error.get("message", "Unknown error")
        else:
            data = result.data
            if isinstance(data, dict):
                preview = build_preview(
                    artifact_id=artifact_id,
                    content_type=str(data.get("content_type", "unknown")),
                    content=data.get("content"),
                )

        return templates.TemplateResponse(
            request=request,
            name="artifacts/detail.html",
            context={
                **_base_ctx,
                "run_id": run_id,
                "artifact_id": artifact_id,
                "adapter_available": True,
                "error": error,
                "preview": preview,
            },
        )

    api_list_path = f"{route_prefix}/api/runs/{{run_id}}/artifacts"

    @app.get(api_list_path, include_in_schema=False)
    async def artifact_list_api(request: Request, run_id: str) -> JSONResponse:
        try:
            validate_run_id(run_id)
        except Exception:
            return JSONResponse(
                {
                    "status": "error",
                    "error": {
                        "code": "invalid_id",
                        "message": f"Invalid run_id: {run_id}",
                    },
                },
                status_code=400,
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            return JSONResponse(
                _adapter_unavailable_response(),
                status_code=503,
            )

        result = adapter.list_artifacts(run_id)
        return JSONResponse(_artifact_list_to_json(result))

    api_detail_path = f"{route_prefix}/api/runs/{{run_id}}/artifacts/{{artifact_id}}"

    @app.get(api_detail_path, include_in_schema=False)
    async def artifact_detail_api(
        request: Request, run_id: str, artifact_id: str
    ) -> JSONResponse:
        try:
            validate_run_id(run_id)
            validate_artifact_id(artifact_id)
        except Exception:
            return JSONResponse(
                {
                    "status": "error",
                    "error": {
                        "code": "invalid_id",
                        "message": "Invalid run_id or artifact_id",
                    },
                },
                status_code=400,
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            return JSONResponse(
                _adapter_unavailable_response(),
                status_code=503,
            )

        result = adapter.read_artifact(run_id, artifact_id)
        if isinstance(result, AdapterErrorResult):
            return JSONResponse(result.to_dict())

        data = result.data
        if not isinstance(data, dict):
            return JSONResponse(
                {
                    "status": "error",
                    "error": {
                        "code": "malformed_adapter_payload",
                        "message": "Adapter returned malformed artifact payload",
                    },
                },
                status_code=502,
            )

        preview = build_preview(
            artifact_id=artifact_id,
            content_type=str(data.get("content_type", "unknown")),
            content=data.get("content"),
        )

        return JSONResponse(_artifact_preview_to_json(result, preview))
