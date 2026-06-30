from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from beeui_module.adapters.envelopes import (
    AdapterErrorResult,
    AdapterResult,
    error_result,
)
from beeui_module.adapters.ids import (
    validate_artifact_id,
    validate_run_id,
    validate_venue_id,
)
from beeui_module.api.envelopes import (
    adapter_unavailable_envelope,
    api_envelope_from_adapter,
    error_status_code,
    invalid_id_envelope,
    malformed_payload_envelope,
    safe_adapter_call,
)
from beeui_module.artifacts.redaction import redact_value
from beeui_module.blocks.layout_renderer import layout_has_charts, render_layout
from beeui_module.pages.locale import resolve_localized_text
from beeui_module.pages.models import BeeUiConfig, BeeUiPage, LocaleConfig
from beeui_module.pages.router import (
    _build_language_switcher,
    build_components_context,
    build_layout_context,
    build_navigation,
    build_shell_classes,
    build_theme_context,
    resolve_locale,
)


def register_product_console_routes(
    *,
    app: FastAPI,
    templates: Jinja2Templates,
    route_prefix: str,
    ui_config: BeeUiConfig,
    product_title: str,
    product_id: str,
) -> list[str]:
    base_context = _build_page_context(
        ui_config,
        route_prefix,
        product_title=product_title,
        product_id=product_id,
    )
    registered = [
        f"{route_prefix or ''}/",
        f"{route_prefix}/runs" if route_prefix else "/runs",
        f"{route_prefix}/runs/{{run_id}}" if route_prefix else "/runs/{run_id}",
        f"{route_prefix}/venues/{{venue_id}}" if route_prefix else "/venues/{venue_id}",
        f"{route_prefix}/api/dashboard" if route_prefix else "/api/dashboard",
        f"{route_prefix}/api/runs" if route_prefix else "/api/runs",
        f"{route_prefix}/api/runs/{{run_id}}" if route_prefix else "/api/runs/{run_id}",
        f"{route_prefix}/api/venues/{{venue_id}}/dashboard"
        if route_prefix
        else "/api/venues/{venue_id}/dashboard",
    ]

    dashboard_path = route_prefix or "/"
    runs_path = f"{route_prefix}/runs" if route_prefix else "/runs"
    run_detail_path = (
        f"{route_prefix}/runs/{{run_id}}" if route_prefix else "/runs/{run_id}"
    )
    venue_path = (
        f"{route_prefix}/venues/{{venue_id}}" if route_prefix else "/venues/{venue_id}"
    )
    api_dashboard_path = (
        f"{route_prefix}/api/dashboard" if route_prefix else "/api/dashboard"
    )
    api_runs_path = f"{route_prefix}/api/runs" if route_prefix else "/api/runs"
    api_run_detail_path = (
        f"{route_prefix}/api/runs/{{run_id}}" if route_prefix else "/api/runs/{run_id}"
    )
    api_venue_path = (
        f"{route_prefix}/api/venues/{{venue_id}}/dashboard"
        if route_prefix
        else "/api/venues/{venue_id}/dashboard"
    )

    @app.get(dashboard_path, response_class=HTMLResponse, include_in_schema=False)
    async def dashboard_html(request: Request) -> HTMLResponse:
        locale = resolve_locale(request, ui_config.locale)
        adapter = _resolve_adapter(request)
        if adapter is None:
            return _render_unavailable(
                request,
                templates,
                "product_dashboard.html",
                base_context,
                title=_resolve_product_page_title(
                    ui_config,
                    path="/",
                    locale=locale,
                    fallback="Dashboard",
                ),
                subtitle=_resolve_product_page_subtitle(
                    ui_config,
                    path="/",
                    locale=locale,
                    fallback="Adapter-backed product overview",
                ),
                active_path="/",
            )

        result = safe_adapter_call(adapter.get_dashboard)
        context, status_code = _dashboard_html_context(
            base_context=base_context,
            active_path="/",
            result=result,
            page_title=_resolve_product_page_title(
                ui_config,
                path="/",
                locale=locale,
                fallback="Dashboard",
            ),
            page_subtitle=_resolve_product_page_subtitle(
                ui_config,
                path="/",
                locale=locale,
                fallback="Adapter-backed product overview",
            ),
        )
        context = _with_request_context(context, request)
        _apply_product_console_labels(context)
        return templates.TemplateResponse(
            request=request,
            name="product_dashboard.html",
            context=context,
            status_code=status_code,
        )

    @app.get(runs_path, response_class=HTMLResponse, include_in_schema=False)
    async def runs_html(request: Request) -> HTMLResponse:
        locale = resolve_locale(request, ui_config.locale)
        adapter = _resolve_adapter(request)
        if adapter is None:
            return _render_unavailable(
                request,
                templates,
                "product_runs.html",
                base_context,
                title=_resolve_product_page_title(
                    ui_config,
                    path="/runs",
                    locale=locale,
                    fallback="Runs",
                ),
                subtitle=_resolve_product_page_subtitle(
                    ui_config,
                    path="/runs",
                    locale=locale,
                    fallback="Adapter-backed run list",
                ),
                active_path="/runs",
            )

        result = safe_adapter_call(adapter.list_runs)
        context, status_code = _runs_html_context(
            base_context=base_context,
            active_path="/runs",
            result=result,
            page_title=_resolve_product_page_title(
                ui_config,
                path="/runs",
                locale=locale,
                fallback="Runs",
            ),
            page_subtitle=_resolve_product_page_subtitle(
                ui_config,
                path="/runs",
                locale=locale,
                fallback="Adapter-backed run list",
            ),
        )
        context = _with_request_context(context, request)
        _apply_product_console_labels(context)
        return templates.TemplateResponse(
            request=request,
            name="product_runs.html",
            context=context,
            status_code=status_code,
        )

    @app.get(run_detail_path, response_class=HTMLResponse, include_in_schema=False)
    async def run_detail_html(request: Request, run_id: str) -> HTMLResponse:
        try:
            validate_run_id(run_id)
        except Exception:
            return _render_invalid_id(
                request,
                templates,
                "product_run_detail.html",
                base_context,
                "run_id",
                run_id,
                active_path="/runs",
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            return _render_unavailable(
                request,
                templates,
                "product_run_detail.html",
                base_context,
                title="Run detail",
                active_path="/runs",
                run_id=run_id,
            )

        result = safe_adapter_call(adapter.get_run, run_id)
        context, status_code = _run_detail_html_context(
            base_context=base_context,
            active_path="/runs",
            run_id=run_id,
            result=result,
        )
        context = _with_request_context(context, request)
        _apply_product_console_labels(context)
        return templates.TemplateResponse(
            request=request,
            name="product_run_detail.html",
            context=context,
            status_code=status_code,
        )

    @app.get(venue_path, response_class=HTMLResponse, include_in_schema=False)
    async def venue_dashboard_html(request: Request, venue_id: str) -> HTMLResponse:
        try:
            validate_venue_id(venue_id)
        except Exception:
            return _render_invalid_id(
                request,
                templates,
                "product_venue_dashboard.html",
                base_context,
                "venue_id",
                venue_id,
                active_path="",
            )

        adapter = _resolve_adapter(request)
        if adapter is None:
            return _render_unavailable(
                request,
                templates,
                "product_venue_dashboard.html",
                base_context,
                title="Venue dashboard",
                active_path="",
                venue_id=venue_id,
            )

        result = _call_optional_adapter_method(
            adapter,
            "get_venue_dashboard",
            venue_id,
        )
        context, status_code = _venue_html_context(
            base_context=base_context,
            active_path="",
            venue_id=venue_id,
            result=result,
        )
        context = _with_request_context(context, request)
        return templates.TemplateResponse(
            request=request,
            name="product_venue_dashboard.html",
            context=context,
            status_code=status_code,
        )

    @app.get(api_dashboard_path, include_in_schema=False)
    async def dashboard_api(request: Request) -> JSONResponse:
        adapter = _resolve_adapter(request)
        if adapter is None:
            payload, status_code = adapter_unavailable_envelope()
            return JSONResponse(payload, status_code=status_code)

        payload, status_code = api_envelope_from_adapter(
            safe_adapter_call(adapter.get_dashboard),
            expected_data_type=dict,
            malformed_message="Adapter returned non-object dashboard payload",
        )
        return JSONResponse(payload, status_code=status_code)

    @app.get(api_runs_path, include_in_schema=False)
    async def runs_api(request: Request) -> JSONResponse:
        adapter = _resolve_adapter(request)
        if adapter is None:
            payload, status_code = adapter_unavailable_envelope()
            return JSONResponse(payload, status_code=status_code)

        payload, status_code = api_envelope_from_adapter(
            _normalize_runs_result_for_api(safe_adapter_call(adapter.list_runs)),
            expected_data_type=list,
            malformed_message="Adapter returned non-list runs payload",
        )
        return JSONResponse(payload, status_code=status_code)

    @app.get(api_run_detail_path, include_in_schema=False)
    async def run_detail_api(request: Request, run_id: str) -> JSONResponse:
        try:
            validate_run_id(run_id)
        except Exception:
            payload, status_code = invalid_id_envelope("run_id", run_id)
            return JSONResponse(payload, status_code=status_code)

        adapter = _resolve_adapter(request)
        if adapter is None:
            payload, status_code = adapter_unavailable_envelope()
            return JSONResponse(payload, status_code=status_code)

        payload, status_code = api_envelope_from_adapter(
            safe_adapter_call(adapter.get_run, run_id),
            expected_data_type=dict,
            malformed_message="Adapter returned non-object run payload",
        )
        return JSONResponse(payload, status_code=status_code)

    @app.get(api_venue_path, include_in_schema=False)
    async def venue_dashboard_api(request: Request, venue_id: str) -> JSONResponse:
        try:
            validate_venue_id(venue_id)
        except Exception:
            payload, status_code = invalid_id_envelope("venue_id", venue_id)
            return JSONResponse(payload, status_code=status_code)

        adapter = _resolve_adapter(request)
        if adapter is None:
            payload, status_code = adapter_unavailable_envelope()
            return JSONResponse(payload, status_code=status_code)

        payload, status_code = api_envelope_from_adapter(
            _call_optional_adapter_method(
                adapter,
                "get_venue_dashboard",
                venue_id,
            ),
            expected_data_type=dict,
            malformed_message=("Adapter returned non-object venue dashboard payload"),
        )
        return JSONResponse(payload, status_code=status_code)

    return registered


def _resolve_adapter(request: Request) -> Any | None:
    return getattr(request.app.state, "beeui_adapter", None)


def _call_optional_adapter_method(
    adapter: Any,
    method_name: str,
    *args: Any,
) -> AdapterResult | AdapterErrorResult:
    method = getattr(adapter, method_name, None)
    if not callable(method):
        return error_result(
            "unavailable",
            f"Adapter method {method_name} is unavailable",
        )
    return safe_adapter_call(method, *args)


def _normalize_runs_result_for_api(
    result: AdapterResult | AdapterErrorResult,
) -> AdapterResult | AdapterErrorResult:
    if not isinstance(result, AdapterResult) or not isinstance(result.data, dict):
        return result
    if not isinstance(result.data.get("layout"), list):
        return result

    runs = result.data.get("runs", result.data.get("items", []))
    if not isinstance(runs, list):
        return result
    return AdapterResult(
        status=result.status,
        data=runs,
        warnings=result.warnings,
        meta=result.meta,
    )


def _resolve_url_prefix(request: Request, route_prefix: str) -> str:
    root_path = str(request.scope.get("root_path") or "").rstrip("/")
    local_prefix = route_prefix.rstrip("/")
    return f"{root_path}{local_prefix}"


def _with_request_context(
    context: dict[str, Any],
    request: Request,
) -> dict[str, Any]:
    route_prefix = str(context.get("route_prefix", ""))
    context["url_prefix"] = _resolve_url_prefix(request, route_prefix)

    locale_cfg = context.get("locale_cfg")
    if isinstance(locale_cfg, LocaleConfig):
        locale = resolve_locale(request, locale_cfg)
        context["locale"] = locale
        context["app_title"] = resolve_localized_text(
            context.get("app_title", ""), locale, locale_cfg.default
        )
        context["logo_text"] = resolve_localized_text(
            context.get("logo_text", ""), locale, locale_cfg.default
        )
        context["language_switcher"] = _build_language_switcher(
            request, locale_cfg, route_prefix
        )

        ui_navigation = context.get("ui_navigation")
        active_path = context.get("active_path")
        if isinstance(ui_navigation, list) and isinstance(active_path, str):
            context["navigation"] = build_navigation(
                route_prefix=route_prefix,
                navigation=ui_navigation,
                active_path=active_path,
                locale=locale,
                default_locale=locale_cfg.default,
            )

    return context


def _build_page_context(
    ui_config: BeeUiConfig,
    route_prefix: str,
    *,
    product_title: str,
    product_id: str,
) -> dict[str, Any]:
    theme = build_theme_context(ui_config)
    layout = build_layout_context(ui_config)
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
        "components": build_components_context(ui_config.components),
        "ui_navigation": ui_config.navigation,
        "navigation": build_navigation(
            route_prefix=route_prefix,
            navigation=ui_config.navigation,
            active_path="/",
            locale=ui_config.locale.default,
            default_locale=ui_config.locale.default,
        ),
        "shell_classes": build_shell_classes(theme, layout),
    }


def _render_unavailable(
    request: Request,
    templates: Jinja2Templates,
    template_name: str,
    base_context: dict[str, Any],
    *,
    title: str,
    subtitle: str | None = None,
    active_path: str,
    run_id: str | None = None,
    venue_id: str | None = None,
) -> HTMLResponse:
    context = dict(base_context)
    context.update(
        {
            "active_path": active_path,
            "navigation": build_navigation(
                route_prefix=base_context["route_prefix"],
                navigation=base_context["ui_navigation"],
                active_path=active_path,
            ),
            "page_title": title,
            "page_subtitle": subtitle,
            "error": "Adapter is not available",
            "warnings": [],
            "meta": {},
            "status": "unavailable",
            "run_id": run_id,
            "venue_id": venue_id,
        }
    )
    context = _with_request_context(context, request)
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context,
        status_code=503,
    )


def _render_invalid_id(
    request: Request,
    templates: Jinja2Templates,
    template_name: str,
    base_context: dict[str, Any],
    field_name: str,
    value: str,
    *,
    active_path: str,
) -> HTMLResponse:
    context = dict(base_context)
    context.update(
        {
            "active_path": active_path,
            "navigation": build_navigation(
                route_prefix=base_context["route_prefix"],
                navigation=base_context["ui_navigation"],
                active_path=active_path,
            ),
            "page_title": "Invalid identifier",
            "page_subtitle": None,
            "error": f"Invalid {field_name}: {value}",
            "warnings": [],
            "meta": {},
            "status": "error",
            field_name: value,
        }
    )
    context = _with_request_context(context, request)
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context,
        status_code=400,
    )


def _dashboard_html_context(
    *,
    base_context: dict[str, Any],
    active_path: str,
    result: AdapterResult | AdapterErrorResult,
    page_title: str,
    page_subtitle: str | None,
) -> tuple[dict[str, Any], int]:
    context = dict(base_context)
    context.update(
        {
            "active_path": active_path,
            "navigation": build_navigation(
                route_prefix=base_context["route_prefix"],
                navigation=base_context["ui_navigation"],
                active_path=active_path,
            ),
            "page_title": page_title,
            "page_subtitle": page_subtitle,
            "warnings": [],
            "meta": {},
            "status": "ok",
            "error": None,
            "dashboard": None,
            "latest_run": None,
            "summary_items": [],
            "kpi_items": [],
        }
    )

    if isinstance(result, AdapterErrorResult):
        code = result.error.get("code", "adapter_error")
        context["status"] = "error"
        context["error"] = str(
            redact_value(result.error.get("message", "Adapter error"))
        )
        context["warnings"] = redact_value(
            [warning.to_dict() for warning in result.warnings]
        )
        context["meta"] = redact_value(result.meta)
        return context, error_status_code(str(code))

    payload = redact_value(result.data)
    if not isinstance(payload, dict):
        payload, status_code = malformed_payload_envelope(
            "Adapter returned non-object dashboard payload"
        )
        context["status"] = "error"
        context["error"] = payload["error"]["message"]
        return context, status_code

    layout = payload.get("layout")
    layout_blocks = render_layout(layout)
    context["layout_blocks"] = layout_blocks
    context["has_layout"] = isinstance(layout, list) and len(layout) > 0
    context["has_charts"] = layout_has_charts(layout_blocks)

    latest_run = (
        payload.get("latest_run")
        if isinstance(payload.get("latest_run"), dict)
        else None
    )
    context["dashboard"] = payload
    context["latest_run"] = _normalize_run_link(latest_run)
    context["summary_items"] = _mapping_items(payload.get("summary"))
    context["kpi_items"] = _normalize_kpi_items(payload.get("kpi_items"))
    context["warnings"] = redact_value(
        [warning.to_dict() for warning in result.warnings]
    )
    context["meta"] = redact_value(result.meta)
    context["status"] = result.status
    return context, 200


def _runs_html_context(
    *,
    base_context: dict[str, Any],
    active_path: str,
    result: AdapterResult | AdapterErrorResult,
    page_title: str,
    page_subtitle: str | None,
) -> tuple[dict[str, Any], int]:
    context = dict(base_context)
    context.update(
        {
            "active_path": active_path,
            "navigation": build_navigation(
                route_prefix=base_context["route_prefix"],
                navigation=base_context["ui_navigation"],
                active_path=active_path,
            ),
            "page_title": page_title,
            "page_subtitle": page_subtitle,
            "warnings": [],
            "meta": {},
            "status": "ok",
            "error": None,
            "runs": [],
        }
    )
    if isinstance(result, AdapterErrorResult):
        code = result.error.get("code", "adapter_error")
        context["status"] = "error"
        context["error"] = str(
            redact_value(result.error.get("message", "Adapter error"))
        )
        context["warnings"] = redact_value(
            [warning.to_dict() for warning in result.warnings]
        )
        context["meta"] = redact_value(result.meta)
        return context, error_status_code(str(code))

    payload = redact_value(result.data)

    if isinstance(payload, dict):
        layout = payload.get("layout")
        layout_blocks = render_layout(layout)
        context["layout_blocks"] = layout_blocks
        context["has_layout"] = isinstance(layout, list) and len(layout) > 0
        context["has_charts"] = layout_has_charts(layout_blocks)
        raw_items = payload.get("runs") or payload.get("items") or []
    elif isinstance(payload, list):
        context["layout_blocks"] = []
        context["has_layout"] = False
        context["has_charts"] = False
        raw_items = payload
    else:
        response, status_code = malformed_payload_envelope(
            "Adapter returned malformed runs payload"
        )
        context["status"] = "error"
        context["error"] = response["error"]["message"]
        return context, status_code

    local_warnings: list[dict[str, str]] = []
    runs: list[dict[str, Any]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            local_warnings.append(
                {
                    "code": "malformed_run_item",
                    "message": "Run item is not an object",
                }
            )
            continue
        safe_run = _normalize_run_link(item)
        if safe_run is None:
            local_warnings.append(
                {
                    "code": "invalid_run_id",
                    "message": "Adapter returned invalid run_id",
                }
            )
            continue
        runs.append(safe_run)

    context["runs"] = runs
    context["warnings"] = redact_value(
        [
            *[warning.to_dict() for warning in result.warnings],
            *local_warnings,
        ]
    )
    context["meta"] = redact_value(result.meta)
    context["status"] = result.status
    return context, 200


def _run_detail_html_context(
    *,
    base_context: dict[str, Any],
    active_path: str,
    run_id: str,
    result: AdapterResult | AdapterErrorResult,
) -> tuple[dict[str, Any], int]:
    context = dict(base_context)
    context.update(
        {
            "active_path": active_path,
            "navigation": build_navigation(
                route_prefix=base_context["route_prefix"],
                navigation=base_context["ui_navigation"],
                active_path=active_path,
            ),
            "page_title": f"Run {run_id}",
            "page_subtitle": "Adapter-backed run detail",
            "warnings": [],
            "meta": {},
            "status": "ok",
            "error": None,
            "run_id": run_id,
            "run": None,
            "artifacts": [],
        }
    )
    if isinstance(result, AdapterErrorResult):
        code = result.error.get("code", "adapter_error")
        context["status"] = "error"
        context["error"] = str(
            redact_value(result.error.get("message", "Adapter error"))
        )
        context["warnings"] = redact_value(
            [warning.to_dict() for warning in result.warnings]
        )
        context["meta"] = redact_value(result.meta)
        return context, error_status_code(str(code))

    payload = redact_value(result.data)
    if not isinstance(payload, dict):
        response, status_code = malformed_payload_envelope(
            "Adapter returned non-object run payload"
        )
        context["status"] = "error"
        context["error"] = response["error"]["message"]
        return context, status_code

    layout = payload.get("layout")
    layout_blocks = render_layout(layout)
    context["layout_blocks"] = layout_blocks
    context["has_layout"] = isinstance(layout, list) and len(layout) > 0
    context["has_charts"] = layout_has_charts(layout_blocks)

    artifacts, local_warnings = _normalize_artifacts(payload.get("artifacts"), run_id)
    context["run"] = payload
    context["artifacts"] = artifacts
    context["warnings"] = redact_value(
        [
            *[warning.to_dict() for warning in result.warnings],
            *local_warnings,
        ]
    )
    context["meta"] = redact_value(result.meta)
    context["status"] = result.status
    return context, 200


def _venue_html_context(
    *,
    base_context: dict[str, Any],
    active_path: str,
    venue_id: str,
    result: AdapterResult | AdapterErrorResult,
) -> tuple[dict[str, Any], int]:
    context = dict(base_context)
    context.update(
        {
            "active_path": active_path,
            "navigation": build_navigation(
                route_prefix=base_context["route_prefix"],
                navigation=base_context["ui_navigation"],
                active_path=active_path,
            ),
            "page_title": f"Venue {venue_id}",
            "page_subtitle": "Adapter-backed venue dashboard",
            "warnings": [],
            "meta": {},
            "status": "ok",
            "error": None,
            "venue_id": venue_id,
            "dashboard": None,
            "summary_items": [],
        }
    )
    if isinstance(result, AdapterErrorResult):
        code = result.error.get("code", "adapter_error")
        context["status"] = "error"
        context["error"] = str(
            redact_value(result.error.get("message", "Adapter error"))
        )
        context["warnings"] = redact_value(
            [warning.to_dict() for warning in result.warnings]
        )
        context["meta"] = redact_value(result.meta)
        return context, error_status_code(str(code))

    payload = redact_value(result.data)
    if not isinstance(payload, dict):
        response, status_code = malformed_payload_envelope(
            "Adapter returned non-object venue dashboard payload"
        )
        context["status"] = "error"
        context["error"] = response["error"]["message"]
        return context, status_code

    layout = payload.get("layout")
    layout_blocks = render_layout(layout)
    context["layout_blocks"] = layout_blocks
    context["has_layout"] = isinstance(layout, list) and len(layout) > 0
    context["has_charts"] = layout_has_charts(layout_blocks)

    context["dashboard"] = payload
    context["summary_items"] = _mapping_items(payload)
    context["warnings"] = redact_value(
        [warning.to_dict() for warning in result.warnings]
    )
    context["meta"] = redact_value(result.meta)
    context["status"] = result.status
    return context, 200


def _resolve_product_page(
    ui_config: BeeUiConfig,
    path: str,
) -> BeeUiPage | None:
    for page in ui_config.pages:
        if page.path == path:
            return page
    return None


def _resolve_product_page_title(
    ui_config: BeeUiConfig,
    *,
    path: str,
    locale: str,
    fallback: str,
) -> str:
    page = _resolve_product_page(ui_config, path)
    if page is None:
        return fallback
    return resolve_localized_text(page.title, locale, ui_config.locale.default)


def _resolve_product_page_subtitle(
    ui_config: BeeUiConfig,
    *,
    path: str,
    locale: str,
    fallback: str | None,
) -> str | None:
    page = _resolve_product_page(ui_config, path)
    if page is not None and page.subtitle is not None:
        return resolve_localized_text(page.subtitle, locale, ui_config.locale.default)
    return fallback


def _product_console_labels(locale: str) -> dict[str, str]:
    if locale == "ru":
        return {
            "latest_run": "Последний запуск",
            "status": "Статус",
            "open_run": "Открыть запуск",
            "kpis": "KPI",
            "summary": "Сводка",
            "technical_details": "Технические детали",
            "run_list": "Список запусков",
            "run_id": "ID запуска",
            "started": "Начат",
            "completed": "Завершён",
            "open": "Открыть",
            "back_to_runs": "Назад к запускам",
        }
    return {
        "latest_run": "Latest run",
        "status": "Status",
        "open_run": "Open run",
        "kpis": "KPIs",
        "summary": "Summary",
        "technical_details": "Technical details",
        "run_list": "Run list",
        "run_id": "Run ID",
        "started": "Started",
        "completed": "Completed",
        "open": "Open",
        "back_to_runs": "Back to runs",
    }


def _apply_product_console_labels(context: dict[str, Any]) -> None:
    locale = str(context.get("locale", "en"))
    context["pc_labels"] = _product_console_labels(locale)


def _normalize_run_link(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    run_id = item.get("id")
    if not isinstance(run_id, str):
        return None
    try:
        validate_run_id(run_id)
    except Exception:
        return None
    normalized = dict(item)
    normalized["id"] = run_id
    normalized["status"] = str(item.get("status", "unknown"))
    return normalized


def _normalize_kpi_items(raw_data: Any) -> list[dict[str, str]]:
    if not isinstance(raw_data, list):
        return []
    normalized: list[dict[str, str]] = []
    for item in raw_data:
        if not isinstance(item, dict):
            continue
        label = item.get("label")
        value = item.get("value")
        if label is None or value is None:
            continue
        normalized.append(
            {
                "label": str(label),
                "value": str(value),
                "status": str(item.get("status", "unknown")),
            }
        )
    return normalized


def _mapping_items(raw_data: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_data, dict):
        return []
    return [{"key": str(key), "value": value} for key, value in raw_data.items()]


def _normalize_artifacts(
    raw_data: Any,
    run_id: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    if not isinstance(raw_data, list):
        return [], []
    artifacts: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
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
                "href": f"{run_id}/artifacts/{artifact_id}",
            }
        )
    return artifacts, warnings
