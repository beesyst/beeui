from __future__ import annotations

from typing import Any

from beeui_module.adapters.envelopes import (
    AdapterErrorResult,
    AdapterResult,
    error_result,
    error_result_from_exception,
)
from beeui_module.artifacts.redaction import redact_value

API_VERSION = "beeui.v0"


def api_success_envelope(
    data: Any,
    *,
    warnings: list[dict[str, Any]] | None = None,
    meta: dict[str, Any] | None = None,
    partial: bool = False,
) -> dict[str, Any]:
    response_meta = dict(meta or {})
    if partial:
        response_meta.setdefault("status", "partial")

    return {
        "ok": True,
        "api": API_VERSION,
        "read_only": True,
        "data": data,
        "warnings": list(warnings or []),
        "meta": response_meta,
    }


def api_error_envelope(
    code: str,
    message: str,
    *,
    warnings: list[dict[str, Any]] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "api": API_VERSION,
        "read_only": True,
        "error": {"code": code, "message": message},
        "warnings": list(warnings or []),
        "meta": dict(meta or {}),
    }


def api_envelope_from_adapter(
    adapter_result: AdapterResult | AdapterErrorResult,
    *,
    expected_data_type: type | tuple[type, ...] | None = None,
    malformed_message: str = "Adapter returned malformed payload",
) -> tuple[dict[str, Any], int]:
    if isinstance(adapter_result, AdapterErrorResult):
        error = adapter_result.error
        code = str(error.get("code", "adapter_error"))
        message = str(redact_value(error.get("message", "Adapter error")))
        return (
            api_error_envelope(
                code,
                message,
                warnings=redact_value(list(adapter_result.to_dict()["warnings"])),
                meta=redact_value(adapter_result.meta),
            ),
            error_status_code(code),
        )

    adapter_payload = adapter_result.to_dict()
    if expected_data_type is not None and not isinstance(
        adapter_payload["data"], expected_data_type
    ):
        return malformed_payload_envelope(malformed_message)

    return (
        api_success_envelope(
            redact_value(adapter_payload["data"]),
            warnings=redact_value(list(adapter_payload["warnings"])),
            meta=redact_value(adapter_payload["meta"]),
            partial=adapter_payload["status"] == "partial",
        ),
        200,
    )


def adapter_unavailable_envelope() -> tuple[dict[str, Any], int]:
    return (
        api_error_envelope("adapter_unavailable", "Adapter is not available"),
        503,
    )


def invalid_id_envelope(field_name: str, value: str) -> tuple[dict[str, Any], int]:
    return (
        api_error_envelope("invalid_id", f"Invalid {field_name}: {value}"),
        400,
    )


def malformed_payload_envelope(message: str) -> tuple[dict[str, Any], int]:
    return api_error_envelope("malformed_adapter_payload", message), 502


def safe_adapter_call(method: Any, *args: Any) -> AdapterResult | AdapterErrorResult:
    try:
        result = method(*args)
    except Exception as exc:
        return error_result_from_exception(exc)

    if isinstance(result, (AdapterResult, AdapterErrorResult)):
        return result

    return error_result(
        "malformed_adapter_payload",
        "Adapter returned malformed result envelope",
    )


def error_status_code(code: str) -> int:
    if code == "invalid_id":
        return 400
    if code == "permission_denied":
        return 403
    if code == "not_found":
        return 404
    if code in {"unavailable", "adapter_unavailable"}:
        return 503
    return 502
