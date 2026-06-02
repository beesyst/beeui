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
from beeui_module.data.selectors import validate_selector

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
def validate_block_definition(
    block_id: str,
    payload: Any,
    available_source_ids: set[str] | None = None,
) -> BlockDefinition:
    if not isinstance(payload, dict):
        raise ValueError(f"blocks.{block_id} must be a mapping")

    _reject_forbidden_keys(payload, f"blocks.{block_id}")

    block_type = _required_non_empty_string(payload, "type", f"blocks.{block_id}")
    if block_type not in ALLOWED_BLOCK_TYPES:
        raise ValueError(
            f"blocks.{block_id}.type must be one of {sorted(ALLOWED_BLOCK_TYPES)}"
        )

    renderer = get_renderer_registry()[block_type]
    source_id, bindings = _validate_selector_bindings(
        block_id,
        block_type,
        payload,
        available_source_ids or set(),
    )
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
        source_id=source_id,
        bindings=bindings,
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


# Принятие разрешенного блока и данных из резолвера, их объединение и повторная валидация для рендера, с учётом возможных ошибок разрешения данных
def coerce_resolved_block(
    block: BlockDefinition,
    resolved_values: dict[str, Any],
    resolution_status: str,
    message: str | None,
) -> BlockDefinition:
    base_payload = {
        key: value
        for key, value in block.payload.items()
        if key not in block.bindings and key != "state"
    }
    merged_payload = {**base_payload, **resolved_values}
    state = _resolved_state(block.state, resolution_status)
    merged_payload = _apply_resolution_defaults(
        block.block_type, merged_payload, message
    )

    raw_payload = {
        "type": block.block_type,
        "title": block.title,
        **merged_payload,
        "state": state,
    }

    try:
        return validate_block_definition(block.block_id, raw_payload)
    except ValueError:
        fallback_message = message or "Resolved data is unavailable."
        fallback_payload = _apply_resolution_defaults(
            block.block_type,
            base_payload,
            fallback_message,
        )
        return validate_block_definition(
            block.block_id,
            {
                "type": block.block_type,
                "title": block.title,
                "state": "error",
                **fallback_payload,
            },
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
        {
            "type",
            "title",
            "value",
            "subtitle",
            "suffix",
            "state",
            "source",
            "value_selector",
            "subtitle_selector",
        },
        f"blocks.{block_id}",
    )
    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
    }
    if "value_selector" in payload:
        value = payload.get("value")
        if value is not None:
            normalized["value"] = _required_display_scalar(
                payload,
                "value",
                f"blocks.{block_id}",
            )
    else:
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
        {"type", "title", "items", "state", "source", "items_selector"},
        f"blocks.{block_id}",
    )
    items = payload.get("items")
    normalized_items: list[dict[str, str]] = []
    if "items_selector" in payload:
        if items is not None:
            normalized_items = _normalize_kpi_items(block_id, items)
    else:
        if not isinstance(items, list):
            raise ValueError(f"blocks.{block_id}.items must be a list")
        normalized_items = _normalize_kpi_items(block_id, items)

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
        {
            "type",
            "title",
            "status",
            "value",
            "subtitle",
            "state",
            "source",
            "status_selector",
            "value_selector",
            "subtitle_selector",
        },
        f"blocks.{block_id}",
    )
    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
    }
    if "status_selector" in payload:
        status = payload.get("status")
        if status is not None:
            normalized["status"] = _validate_status_value(status, block_id)
    else:
        normalized["status"] = _validate_status_value(
            _required_non_empty_string(payload, "status", f"blocks.{block_id}"),
            block_id,
        )
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
        {
            "type",
            "title",
            "columns",
            "rows",
            "empty",
            "state",
            "source",
            "rows_selector",
        },
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
    normalized_rows: list[dict[str, str]] = []
    if "rows_selector" in payload:
        if rows is not None:
            normalized_rows = _normalize_table_rows(block_id, rows)
    else:
        if not isinstance(rows, list):
            raise ValueError(f"blocks.{block_id}.rows must be a list")
        normalized_rows = _normalize_table_rows(block_id, rows)

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
        {"type", "title", "text", "state", "source", "text_selector"},
        f"blocks.{block_id}",
    )
    normalized = {
        "title": _required_non_empty_string(payload, "title", f"blocks.{block_id}"),
    }
    if "text_selector" in payload:
        text = payload.get("text")
        if text is not None:
            normalized["text"] = _required_non_empty_string(
                payload,
                "text",
                f"blocks.{block_id}",
            )
    else:
        normalized["text"] = _required_non_empty_string(
            payload,
            "text",
            f"blocks.{block_id}",
        )
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


# Нормализация items для kpi_grid, включая валидацию статусов и чек на отсутствие HTML/JS в label/value
def _normalize_kpi_items(block_id: str, items: Any) -> list[dict[str, str]]:
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

    return normalized_items


# Нормализация rows для table_card, включая чек на отсутствие HTML/JS в ячейках и требование scalar values для безопасного отображения
def _normalize_table_rows(block_id: str, rows: Any) -> list[dict[str, str]]:
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

    return normalized_rows


# Валидация статуса для status_card, ограниченного безопасным набором значений, с учётом возможного получения из резолвера
def _validate_status_value(status: Any, block_id: str) -> str:
    if not isinstance(status, str) or status not in _ALLOWED_STATUS_VALUES:
        raise ValueError(
            f"blocks.{block_id}.status must be one of {sorted(_ALLOWED_STATUS_VALUES)}"
        )
    return status


# Валидация селекторных полей и их связка с source, включая чек на существование source_id в доступных источниках данных
def _validate_selector_bindings(
    block_id: str,
    block_type: str,
    payload: dict[str, Any],
    available_source_ids: set[str],
) -> tuple[str | None, dict[str, str]]:
    selector_fields = _selector_fields_for_block(block_type)
    bindings: dict[str, str] = {}

    for selector_key, target_field in selector_fields.items():
        selector_value = payload.get(selector_key)
        if selector_value is None:
            continue
        if not isinstance(selector_value, str) or not selector_value.strip():
            raise ValueError(
                f"blocks.{block_id}.{selector_key} must be a non-empty string"
            )
        try:
            validate_selector(selector_value)
        except ValueError:
            raise ValueError(
                f"blocks.{block_id}.{selector_key} must be a valid selector"
            ) from None
        bindings[target_field] = selector_value.strip()

    source_id = payload.get("source")
    if source_id is None:
        if bindings:
            raise ValueError(
                f"blocks.{block_id}.source must be provided when selector fields are used"
            )
        return None, {}

    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError(f"blocks.{block_id}.source must be a non-empty string")
    if not bindings:
        raise ValueError(
            f"blocks.{block_id}.source requires at least one selector field"
        )
    if source_id not in available_source_ids:
        raise ValueError(
            f"blocks.{block_id}.source references an unknown data source: {source_id}"
        )

    return source_id.strip(), bindings


# Валидация блока страницы: чек наличия block, width и их правильного типа, а также ссылки на объявленный block id в реестре
def _selector_fields_for_block(block_type: str) -> dict[str, str]:
    return {
        "metric_card": {
            "value_selector": "value",
            "subtitle_selector": "subtitle",
        },
        "kpi_grid": {"items_selector": "items"},
        "status_card": {
            "status_selector": "status",
            "value_selector": "value",
            "subtitle_selector": "subtitle",
        },
        "table_card": {"rows_selector": "rows"},
        "text_card": {"text_selector": "text"},
    }.get(block_type, {})


# Чек наличия block, width и их правильного типа, а также ссылки на объявленный block id в реестре
def _resolved_state(existing_state: str, resolution_status: str) -> str:
    if resolution_status == "error":
        return "error"
    if resolution_status == "partial" and existing_state == "normal":
        return "degraded"
    return existing_state


# Чек наличия block, width и их правильного типа, а также ссылки на объявленный block id в реестре
def _apply_resolution_defaults(
    block_type: str,
    payload: dict[str, Any],
    message: str | None,
) -> dict[str, Any]:
    normalized = dict(payload)
    fallback_message = message or "Resolved data is unavailable."

    if block_type == "metric_card":
        normalized.setdefault("value", "Unavailable")
        normalized.setdefault("subtitle", fallback_message)
        return normalized
    if block_type == "status_card":
        normalized.setdefault("status", "degraded")
        normalized.setdefault("value", "Unavailable")
        normalized.setdefault("subtitle", fallback_message)
        return normalized
    if block_type == "text_card":
        normalized.setdefault("text", fallback_message)
        return normalized
    if block_type == "table_card":
        normalized.setdefault("columns", [])
        normalized.setdefault("rows", [])
        normalized.setdefault("empty", fallback_message)
        return normalized
    if block_type == "kpi_grid":
        normalized.setdefault("items", [])
        return normalized

    return normalized
