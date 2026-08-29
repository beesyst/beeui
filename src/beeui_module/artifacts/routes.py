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
from beeui_module.api.envelopes import async_safe_adapter_call
from beeui_module.artifacts.models import ArtifactPreview
from beeui_module.artifacts.preview import build_preview
from beeui_module.pages.links import effective_external_prefix, prefix_internal_href
from beeui_module.pages.locale import (
    resolve_locale as _resolve_locale,
)
from beeui_module.pages.locale import (
    resolve_localized_text,
)
from beeui_module.pages.models import BeeUiConfig
from beeui_module.pages.router import (
    _build_language_switcher,
    build_layout_context,
    build_navigation,
    build_shell_classes,
    build_theme_context,
)


def _resolve_adapter(request: Request) -> Any | None:
    return getattr(request.app.state, "beeui_adapter", None)


def _adapter_unavailable_response() -> dict[str, Any]:
    return {
        "status": "error",
        "error": {"code": "adapter_unavailable", "message": "Adapter is not available"},
    }


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


def _build_page_context(
    ui_config: BeeUiConfig,
    route_prefix: str,
    *,
    product_title: str,
    product_id: str,
) -> dict[str, Any]:
    theme = build_theme_context(ui_config)
    layout = build_layout_context(ui_config)
    shell_classes = build_shell_classes(theme, layout)

    return {
        "route_prefix": route_prefix,
        "app_title": ui_config.app_title,
        "product_title": product_title,
        "product_id": product_id,
        "logo_text": ui_config.logo_text,
        "locale_cfg": ui_config.locale,
        "available_locales": list(ui_config.locale.available),
        "theme": theme,
        "layout": layout,
        "shell_classes": shell_classes,
    }


def _inject_locale_context(
    ctx: dict[str, Any],
    request: Request,
    ui_config: BeeUiConfig | None,
    route_prefix: str,
) -> None:
    if ui_config is None:
        ctx.setdefault("locale", "en")
        ctx.setdefault("language_switcher", None)
        return

    locale = _resolve_locale(
        request, ui_config.locale.default, ui_config.locale.available
    )
    ctx["locale"] = locale
    ctx["language_switcher"] = _build_language_switcher(
        request, ui_config.locale, route_prefix
    )
    ctx["navigation"] = build_navigation(
        route_prefix=route_prefix,
        navigation=ui_config.navigation,
        active_path="",
        locale=locale,
        default_locale=ui_config.locale.default,
    )
    ctx["app_title"] = resolve_localized_text(
        ctx.get("app_title", ui_config.app_title)
        if isinstance(ctx.get("app_title"), str)
        else ui_config.app_title,
        locale,
        ui_config.locale.default,
    )
    ctx["logo_text"] = resolve_localized_text(
        ctx.get("logo_text", ui_config.logo_text)
        if isinstance(ctx.get("logo_text"), str)
        else ui_config.logo_text,
        locale,
        ui_config.locale.default,
    )


def _prepare_html_context(
    base: dict[str, Any],
    request: Request,
    ui_config: BeeUiConfig | None,
    route_prefix: str,
) -> tuple[dict[str, Any], str]:
    external_prefix = effective_external_prefix(request, route_prefix)
    ctx = {**base, "route_prefix": external_prefix}
    ctx["runs_href"] = prefix_internal_href(external_prefix, "/runs")
    _inject_locale_context(ctx, request, ui_config, external_prefix)
    return ctx, external_prefix


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
            ctx, _ = _prepare_html_context(_base_ctx, request, ui_config, route_prefix)
            ctx.update(
                {
                    "run_id": run_id,
                    "artifacts": [],
                    "adapter_available": False,
                    "error": f"Invalid run_id: {run_id}",
                }
            )
            return templates.TemplateResponse(
                request=request,
                name="artifacts/list.html",
                status_code=400,
                context=ctx,
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            ctx, _ = _prepare_html_context(_base_ctx, request, ui_config, route_prefix)
            ctx.update(
                {
                    "run_id": run_id,
                    "artifacts": [],
                    "adapter_available": False,
                    "error": "Adapter is not available",
                }
            )
            return templates.TemplateResponse(
                request=request,
                name="artifacts/list.html",
                status_code=503,
                context=ctx,
            )

        result = await async_safe_adapter_call(adapter.list_artifacts, run_id)
        error: str | None = None
        artifacts: list[dict[str, Any]] = []

        if isinstance(result, AdapterErrorResult):
            error = result.error.get("message", "Unknown error")
        else:
            raw_data = result.data
            if isinstance(raw_data, list):
                artifacts, _warnings = _normalize_artifact_items(result.data)

        ctx, external_prefix = _prepare_html_context(
            _base_ctx, request, ui_config, route_prefix
        )
        for artifact in artifacts:
            artifact["href"] = prefix_internal_href(
                external_prefix,
                f"/runs/{run_id}/artifacts/{artifact['artifact_id']}",
            )
        ctx.update(
            {
                "run_id": run_id,
                "artifacts": artifacts,
                "adapter_available": True,
                "error": error,
                "runs_href": prefix_internal_href(external_prefix, "/runs"),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="artifacts/list.html",
            context=ctx,
        )

    detail_html_path = f"{route_prefix}/runs/{{run_id}}/artifacts/{{artifact_id}}"

    @app.get(detail_html_path, response_class=HTMLResponse, include_in_schema=False)
    async def artifact_detail_html(
        request: Request, run_id: str, artifact_id: str
    ) -> HTMLResponse:
        try:
            validate_run_id(run_id)
            validate_artifact_id(artifact_id)
        except Exception:
            ctx, external_prefix = _prepare_html_context(
                _base_ctx, request, ui_config, route_prefix
            )
            ctx.update(
                {
                    "run_id": run_id,
                    "artifact_id": artifact_id,
                    "adapter_available": False,
                    "error": "Invalid run_id or artifact_id",
                    "preview": None,
                    "artifacts_href": prefix_internal_href(
                        external_prefix, f"/runs/{run_id}/artifacts"
                    ),
                }
            )
            return templates.TemplateResponse(
                request=request,
                name="artifacts/detail.html",
                status_code=400,
                context=ctx,
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            ctx, external_prefix = _prepare_html_context(
                _base_ctx, request, ui_config, route_prefix
            )
            ctx.update(
                {
                    "run_id": run_id,
                    "artifact_id": artifact_id,
                    "adapter_available": False,
                    "error": "Adapter is not available",
                    "preview": None,
                    "artifacts_href": prefix_internal_href(
                        external_prefix, f"/runs/{run_id}/artifacts"
                    ),
                }
            )
            return templates.TemplateResponse(
                request=request,
                name="artifacts/detail.html",
                status_code=503,
                context=ctx,
            )

        result = await async_safe_adapter_call(
            adapter.read_artifact,
            run_id,
            artifact_id,
        )
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

        ctx, external_prefix = _prepare_html_context(
            _base_ctx, request, ui_config, route_prefix
        )
        ctx.update(
            {
                "run_id": run_id,
                "artifact_id": artifact_id,
                "adapter_available": True,
                "error": error,
                "preview": preview,
                "artifacts_href": prefix_internal_href(
                    external_prefix, f"/runs/{run_id}/artifacts"
                ),
            }
        )
        return templates.TemplateResponse(
            request=request,
            name="artifacts/detail.html",
            context=ctx,
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

        result = await async_safe_adapter_call(adapter.list_artifacts, run_id)
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

        result = await async_safe_adapter_call(
            adapter.read_artifact,
            run_id,
            artifact_id,
        )
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
