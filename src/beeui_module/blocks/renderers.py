from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from beeui_module.blocks.models import (
    ALLOWED_BLOCK_STATES,
    ALLOWED_BLOCK_TYPES,
    BlockDefinition,
    RenderedBlock,
)

_SAFE_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_FORBIDDEN_SCHEMA_KEYS = {
    "html",
    "script",
    "javascript",
    "style",
    "css",
    "custom_css",
    "custom_js",
}
_ALLOWED_STATUS_VALUES = {
    "ok",
    "warning",
    "error",
    "unknown",
    "partial",
    "degraded",
    "unavailable",
    "disabled",
}
_ALLOWED_ALERT_SEVERITIES = {"info", "warning", "error", "success"}
_ALLOWED_KPI_STATUSES = {"ok", "warning", "error", "unknown", "partial", "degraded"}


# Описание renderer: имя template и функция проверки payload
@dataclass(frozen=True)
class BlockRenderer:
    template_name: str
    validator: Any


# Валидация schema block и нормализация payload для дальнейшего рендера
def validate_block_definition(block_id: str, payload: Any) -> BlockDefinition:
    if not isinstance(payload, dict):
        raise ValueError(f"blocks.{block_id} must be a mapping")

    _reject_forbidden_keys(payload, f"blocks.{block_id}")

    block_type = _required_non_empty_string(payload, "type", f"blocks.{block_id}")
    if block_type not in ALLOWED_BLOCK_TYPES:
        raise ValueError(
            f"blocks.{block_id}.type must be one of {sorted(ALLOWED_BLOCK_TYPES)}"
        )

    renderer = get_renderer_registry()[block_type]
    normalized_payload = renderer.validator(block_id, payload)

    title = normalized_payload["title"]
    state = normalized_payload.get("state", "normal")
    if state not in ALLOWED_BLOCK_STATES:
        raise ValueError(
            f"blocks.{block_id}.state must be one of {sorted(ALLOWED_BLOCK_STATES)}"
        )

    return BlockDefinition(
        block_id=block_id,
        block_type=block_type,
        title=title,
        state=state,
        payload=normalized_payload,
    )


# Подбор template для уже валидированного блока
def render_block(block: BlockDefinition, width: int) -> RenderedBlock:
    renderer = get_renderer_registry()[block.block_type]
    return RenderedBlock(
        block_id=block.block_id,
        block_type=block.block_type,
        title=block.title,
        state=block.state,
        width=width,
        template_name=renderer.template_name,
        payload=block.payload,
    )


# Единый список поддерживаемых block types
def get_renderer_registry() -> dict[str, BlockRenderer]:
    return {
        "metric_card": BlockRenderer(
            template_name="components/metric_card.html",
            validator=_validate_metric_card,
        ),
        "kpi_grid": BlockRenderer(
            template_name="components/kpi_grid.html",
            validator=_validate_kpi_grid,
        ),
        "status_card": BlockRenderer(
            template_name="components/status_card.html",
            validator=_validate_status_card,
        ),
        "table_card": BlockRenderer(
            template_name="components/table_card.html",
            validator=_validate_table_card,
        ),
        "links_card": BlockRenderer(
            template_name="components/links_card.html",
            validator=_validate_links_card,
        ),
        "alert_card": BlockRenderer(
            template_name="components/alert_card.html",
            validator=_validate_alert_card,
        ),
        "text_card": BlockRenderer(
            template_name="components/text_card.html",
            validator=_validate_text_card,
        ),
        "progress_card": BlockRenderer(
            template_name="components/progress_card.html",
            validator=_validate_progress_card,
        ),
    }


# Чек metric_card: обязательные title/value и опциональные subtitle/suffix
def _validate_metric_card(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "value", "subtitle", "suffix", "state"},
        f"blocks.{block_id}",
    )
    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "value": _required_display_scalar(payload, "value", f"blocks.{block_id}"),
    }
    subtitle = payload.get("subtitle")
    if subtitle is not None:
        normalized["subtitle"] = _required_non_empty_string(
            payload,
            "subtitle",
            f"blocks.{block_id}",
        )
    suffix = payload.get("suffix")
    if suffix is not None:
        normalized["suffix"] = _required_non_empty_string(
            payload,
            "suffix",
            f"blocks.{block_id}",
        )
    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек kpi_grid: список KPI с label/value и опциональным status
def _validate_kpi_grid(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "items", "state"},
        f"blocks.{block_id}",
    )
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError(f"blocks.{block_id}.items must be a list")

    normalized_items: list[dict[str, str]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"blocks.{block_id}.items[{index}] must be a mapping")
        _validate_exact_keys(
            item,
            {"label", "value", "status"},
            f"blocks.{block_id}.items[{index}]",
        )
        normalized_item = {
            "label": _required_non_empty_string(
                item,
                "label",
                f"blocks.{block_id}.items[{index}]",
            ),
            "value": _required_display_scalar(
                item,
                "value",
                f"blocks.{block_id}.items[{index}]",
            ),
        }
        status = item.get("status")
        if status is not None:
            if not isinstance(status, str) or status not in _ALLOWED_KPI_STATUSES:
                raise ValueError(
                    f"blocks.{block_id}.items[{index}].status must be one of {sorted(_ALLOWED_KPI_STATUSES)}"
                )
            normalized_item["status"] = status
        normalized_items.append(normalized_item)

    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "items": normalized_items,
    }
    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек status_card: status ограничен безопасным набором CSS-состояний
def _validate_status_card(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "status", "value", "subtitle", "state"},
        f"blocks.{block_id}",
    )
    status = _required_non_empty_string(payload, "status", f"blocks.{block_id}")
    if status not in _ALLOWED_STATUS_VALUES:
        raise ValueError(
            f"blocks.{block_id}.status must be one of {sorted(_ALLOWED_STATUS_VALUES)}"
        )

    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "status": status,
    }
    value = payload.get("value")
    if value is not None:
        normalized["value"] = _required_display_scalar(
            payload,
            "value",
            f"blocks.{block_id}",
        )
    subtitle = payload.get("subtitle")
    if subtitle is not None:
        normalized["subtitle"] = _required_non_empty_string(
            payload,
            "subtitle",
            f"blocks.{block_id}",
        )
    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек table_card: колонки фиксируют порядок, rows принимают только scalar values
def _validate_table_card(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "columns", "rows", "empty", "state"},
        f"blocks.{block_id}",
    )

    columns = payload.get("columns")
    if not isinstance(columns, list) or not columns:
        raise ValueError(f"blocks.{block_id}.columns must be a non-empty list")

    normalized_columns: list[dict[str, str]] = []
    for index, column in enumerate(columns):
        if not isinstance(column, dict):
            raise ValueError(f"blocks.{block_id}.columns[{index}] must be a mapping")
        _validate_exact_keys(
            column,
            {"key", "label"},
            f"blocks.{block_id}.columns[{index}]",
        )
        normalized_columns.append(
            {
                "key": _required_non_empty_string(
                    column,
                    "key",
                    f"blocks.{block_id}.columns[{index}]",
                ),
                "label": _required_non_empty_string(
                    column,
                    "label",
                    f"blocks.{block_id}.columns[{index}]",
                ),
            }
        )

    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"blocks.{block_id}.rows must be a list")

    normalized_rows: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"blocks.{block_id}.rows[{index}] must be a mapping")
        normalized_row: dict[str, str] = {}
        for key, value in row.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(
                    f"blocks.{block_id}.rows[{index}] contains invalid key"
                )
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError(
                    f"blocks.{block_id}.rows[{index}].{key} must be a scalar value"
                )
            normalized_row[key] = str(value)
        normalized_rows.append(normalized_row)

    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "columns": normalized_columns,
        "rows": normalized_rows,
    }

    empty = payload.get("empty")
    if empty is not None:
        normalized["empty"] = _required_non_empty_string(
            payload,
            "empty",
            f"blocks.{block_id}",
        )

    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек links_card: href разрешён только как внутренний безопасный path
def _validate_links_card(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "links", "state"},
        f"blocks.{block_id}",
    )
    links = payload.get("links")
    if not isinstance(links, list):
        raise ValueError(f"blocks.{block_id}.links must be a list")

    normalized_links: list[dict[str, str]] = []
    for index, link in enumerate(links):
        if not isinstance(link, dict):
            raise ValueError(f"blocks.{block_id}.links[{index}] must be a mapping")
        _validate_exact_keys(
            link,
            {"label", "href"},
            f"blocks.{block_id}.links[{index}]",
        )
        href = _required_non_empty_string(
            link,
            "href",
            f"blocks.{block_id}.links[{index}]",
        )
        normalized_links.append(
            {
                "label": _required_non_empty_string(
                    link,
                    "label",
                    f"blocks.{block_id}.links[{index}]",
                ),
                "href": _safe_internal_href(
                    href,
                    f"blocks.{block_id}.links[{index}].href",
                ),
            }
        )

    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "links": normalized_links,
    }
    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек alert_card: severity ограничен локальными визуальными вариантами
def _validate_alert_card(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "message", "severity", "state"},
        f"blocks.{block_id}",
    )
    severity = _required_non_empty_string(payload, "severity", f"blocks.{block_id}")
    if severity not in _ALLOWED_ALERT_SEVERITIES:
        raise ValueError(
            f"blocks.{block_id}.severity must be one of {sorted(_ALLOWED_ALERT_SEVERITIES)}"
        )

    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "message": _required_non_empty_string(payload, "message", f"blocks.{block_id}"),
        "severity": severity,
    }
    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек text_card: только plain text, без markdown/html интерпретации
def _validate_text_card(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "text", "state"},
        f"blocks.{block_id}",
    )
    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "text": _required_non_empty_string(payload, "text", f"blocks.{block_id}"),
    }
    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек progress_card: value должен быть процентом в диапазоне 0..100
def _validate_progress_card(block_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    _validate_exact_keys(
        payload,
        {"type", "title", "value", "label", "state"},
        f"blocks.{block_id}",
    )
    value = payload.get("value")
    if not isinstance(value, int) or value < 0 or value > 100:
        raise ValueError(f"blocks.{block_id}.value must be an integer in range 0..100")

    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
        "value": value,
    }
    label = payload.get("label")
    if label is not None:
        normalized["label"] = _required_non_empty_string(
            payload,
            "label",
            f"blocks.{block_id}",
        )

    state = payload.get("state", "normal")
    _validate_state(state, f"blocks.{block_id}")
    normalized["state"] = state
    return normalized


# Чек общие состояния блока, отображаемые всеми templates
def _validate_state(state: Any, prefix: str) -> None:
    if not isinstance(state, str) or state not in ALLOWED_BLOCK_STATES:
        raise ValueError(
            f"{prefix}.state must be one of {sorted(ALLOWED_BLOCK_STATES)}"
        )


# Возврат непустой строки без сохранения внешних пробелов
def _required_non_empty_string(payload: dict[str, Any], key: str, prefix: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{prefix}.{key} must be a non-empty string")
    return value.strip()


# Возврат scalar value как строки для безопасного HTML-вывода через Jinja autoescape
def _required_display_scalar(
    payload: dict[str, Any],
    key: str,
    prefix: str,
) -> str:
    value = payload.get(key)
    if not isinstance(value, (str, int, float, bool)):
        raise ValueError(f"{prefix}.{key} must be a scalar value")
    display_value = str(value).strip()
    if not display_value:
        raise ValueError(f"{prefix}.{key} must be a non-empty scalar value")
    return display_value


# Блок schema keys, которые могли бы намекать на HTML/CSS/JS injection
def _reject_forbidden_keys(payload: dict[str, Any], prefix: str) -> None:
    forbidden = sorted(set(payload) & _FORBIDDEN_SCHEMA_KEYS)
    if forbidden:
        raise ValueError(f"{prefix} contains unsupported keys: {', '.join(forbidden)}")


# Fail-fast чек, что schema не содержит неизвестных полей
def _validate_exact_keys(
    payload: dict[str, Any], allowed_keys: set[str], prefix: str
) -> None:
    unknown = sorted(set(payload) - allowed_keys)
    if unknown:
        raise ValueError(f"{prefix} contains unsupported keys: {', '.join(unknown)}")


# Принятие только внутренних path-линков без query/hash/traversal
def _safe_internal_href(value: str, field_name: str) -> str:
    lowered = value.lower()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        raise ValueError(f"{field_name} must be an internal path")
    if lowered.startswith("mailto:"):
        raise ValueError(f"{field_name} must be an internal path")
    if lowered.startswith("javascript:"):
        raise ValueError(f"{field_name} must be an internal path")

    if not value.startswith("/"):
        raise ValueError(f"{field_name} must start with '/'")
    if value == "/":
        return value
    if value.startswith("//") or value.endswith("/"):
        raise ValueError(f"{field_name} must be a safe path")
    if "?" in value or "#" in value or "\\" in value:
        raise ValueError(f"{field_name} must be a safe path")

    segments = value.split("/")[1:]
    for segment in segments:
        if segment in {"", ".", ".."}:
            raise ValueError(f"{field_name} must be a safe path")
        if not _SAFE_SEGMENT_RE.fullmatch(segment):
            raise ValueError(f"{field_name} must be a safe path")

    return value
