from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any

from beeui_module.pages.links import prefix_internal_href, validate_internal_href

_WIDTH_MAP: dict[int, str] = {
    12: "col-12",
    8: "col-12 col-lg-8",
    6: "col-12 col-lg-6",
    4: "col-12 col-md-6 col-lg-4",
    3: "col-12 col-sm-6 col-lg-3",
    2: "col-12 col-sm-6 col-lg-2",
}
_SIZE_MAP: dict[str, int] = {
    "S": 4,
    "M": 6,
    "L": 8,
    "XL": 12,
}
_DEFAULT_WIDTH_CLASS = "col-12"
_SUPPORTED_BLOCK_TYPES: set[str] = {
    "hero_snapshot",
    "metric_card",
    "kpi_strip",
    "venue_summary_grid",
    "mode_cards",
    "status_table",
    "event_table",
    "attention_list",
    "artifact_links",
    "raw_json_panel",
    "chart",
    "operator_hero",
    "venue_card",
    "kpi_grid",
    "state_grid",
    "quick_links",
    "run_table",
    "group",
    "data_table",
    "filter_form",
}
_RUN_TABLE_COLUMNS: tuple[str, ...] = (
    "Run",
    "Mode",
    "Venue",
    "Symbol",
    "TF",
    "Started UTC",
    "Health",
    "Event Time UTC",
    "Event",
    "Severity",
    "Events",
    "Artifact",
)
_KPI_GRID_COLUMN_CLASSES: dict[int, str] = {
    1: "col-12",
    2: "col-12 col-sm-6",
    3: "col-12 col-sm-6 col-lg-4",
    4: "col-12 col-sm-6 col-lg-3",
}
_GROUP_MAX_DEPTH: int = 3
_CHART_COLOR_TOKENS: frozenset[str] = frozenset(
    {
        "primary",
        "secondary",
        "success",
        "warning",
        "danger",
        "info",
        "blue",
        "azure",
        "indigo",
        "purple",
        "pink",
        "red",
        "orange",
        "yellow",
        "lime",
        "green",
        "teal",
        "cyan",
    }
)
_CHART_COLOR_LIMIT = 12
_CHART_HEX_COLOR_PATTERN = re.compile(r"#[0-9A-Fa-f]{6}")
_CHART_ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
_DATA_TABLE_ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
_BAR_HEIGHT_PATTERN = re.compile(r"(?:[1-9]|[1-9][0-9]|100)%")
_CHART_DISPLAY_VALUE_LIMIT = 100
_CHART_DISPLAY_TEXT_LIMIT = 256
_PROGRESS_TONES: frozenset[str] = frozenset(
    {"bg-primary", "bg-secondary", "bg-success", "bg-warning", "bg-danger", "bg-info"}
)


def _resolve_width_class(width: Any) -> str:
    if isinstance(width, int) and width in _WIDTH_MAP:
        return _WIDTH_MAP[width]
    return _DEFAULT_WIDTH_CLASS


def _resolve_block_width_class(raw: dict[str, Any]) -> str:
    has_width = "width" in raw
    has_span = "span" in raw
    has_size = "size" in raw

    count = sum([has_width, has_span, has_size])
    if count > 1:
        return _DEFAULT_WIDTH_CLASS

    if has_span:
        span = raw["span"]
        if isinstance(span, int) and span in _WIDTH_MAP:
            return _WIDTH_MAP[span]
        return _DEFAULT_WIDTH_CLASS

    if has_size:
        size = raw["size"]
        if isinstance(size, str) and size.upper() in _SIZE_MAP:
            span = _SIZE_MAP[size.upper()]
            return _WIDTH_MAP[span]
        return _DEFAULT_WIDTH_CLASS

    return _resolve_width_class(raw.get("width"))


def _safe_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return ""


def _display_value(value: Any, default: str = "n/a") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        clean = value.strip()
        if clean.lower() in {"", "none", "null"}:
            return default
        return clean
    if isinstance(value, (int, float, bool)):
        return str(value)
    return default


def _safe_list(raw: Any) -> list[Any]:
    if isinstance(raw, list):
        return raw
    return []


def _safe_dict_list(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _normalize_chart_colors(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    colors: list[str] = []
    for token in value:
        if isinstance(token, str) and token in _CHART_COLOR_TOKENS:
            colors.append(f"var(--tblr-{token})")
        elif isinstance(token, str) and _CHART_HEX_COLOR_PATTERN.fullmatch(token):
            colors.append(token)
        else:
            continue
        if len(colors) == _CHART_COLOR_LIMIT:
            break
    return colors


def _is_finite_chart_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def _normalize_chart_display_values(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    values: list[str] = []
    for item in value:
        if isinstance(item, str):
            text = item
        elif _is_finite_chart_number(item):
            text = str(item)
        else:
            continue
        values.append(text[:_CHART_DISPLAY_TEXT_LIMIT])
        if len(values) == _CHART_DISPLAY_VALUE_LIMIT:
            break
    return values


def _normalize_chart_series(kind: str | None, value: Any) -> tuple[list[Any], str]:
    if value is None:
        return [], "empty"
    if not isinstance(value, list):
        return [], "degraded"
    if not value:
        return [], "empty"
    if kind == "donut":
        if not all(_is_finite_chart_number(item) for item in value):
            return [], "degraded"
        return list(value), "ready"

    normalized: list[dict[str, Any]] = []
    has_data = False
    for item in value:
        if not isinstance(item, dict):
            return [], "degraded"
        name = item.get("name")
        data = item.get("data")
        if not isinstance(name, str) or not name.strip() or not isinstance(data, list):
            return [], "degraded"
        if not all(_is_finite_chart_number(point) for point in data):
            return [], "degraded"
        normalized.append(
            {"name": name.strip()[:_CHART_DISPLAY_TEXT_LIMIT], "data": list(data)}
        )
        has_data = has_data or bool(data)
    return normalized, "ready" if has_data else "empty"


def _normalize_chart_id(value: Any, title: str, config: dict[str, Any]) -> str:
    if isinstance(value, str) and _CHART_ID_PATTERN.fullmatch(value):
        return value
    return _chart_id_from_config(title, config)


def _safe_table_rows(raw: Any, column_count: int) -> list[list[str]]:
    if not isinstance(raw, list):
        raise ValueError("Block rows are missing or invalid")

    rows: list[list[str]] = []
    for row in raw:
        if not isinstance(row, list) or len(row) != column_count:
            raise ValueError("Block row shape is invalid")
        rows.append([_safe_str(cell) for cell in row])
    return rows


def _safe_columns(raw: Any) -> list[str]:
    if (
        not isinstance(raw, list)
        or not raw
        or not all(isinstance(column, str) for column in raw)
    ):
        raise ValueError("Block columns are missing or invalid")
    return list(raw)


def _safe_run_table_columns(raw: Any) -> list[str]:
    columns = _safe_columns(raw)
    if tuple(columns) != _RUN_TABLE_COLUMNS:
        raise ValueError("Run table columns must match the operator contract")
    return columns


def _require_title(raw: dict[str, Any]) -> None:
    if not isinstance(raw.get("title"), str) or not raw["title"].strip():
        raise ValueError("Block title is missing or invalid")


def _require_list(raw: dict[str, Any], field: str) -> None:
    if not isinstance(raw.get(field), list):
        raise ValueError(f"Block {field} is missing or invalid")


def _require_scalar(raw: dict[str, Any], field: str) -> None:
    if not isinstance(raw.get(field), (str, int, float, bool)):
        raise ValueError(f"Block {field} is missing or invalid")


def resolve_kpi_grid_columns(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        if value in _KPI_GRID_COLUMN_CLASSES:
            return value
    return 4


def _render_block(raw: Any, depth: int = _GROUP_MAX_DEPTH) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return _degraded_block("Block is not an object", width=None)

    block_type = raw.get("type")
    if not isinstance(block_type, str) or not block_type:
        return _degraded_block("Block type is missing or invalid", width=raw)

    if block_type not in _SUPPORTED_BLOCK_TYPES:
        return _degraded_block(
            f"Unsupported block type: {block_type}",
            width=raw,
        )

    width_class = _resolve_block_width_class(raw)

    try:
        renderer = _BLOCK_RENDERERS[block_type]
        if block_type == "group":
            return renderer(raw, width_class, depth=depth)
        return renderer(raw, width_class)
    except Exception:
        return _degraded_block(
            f"Failed to render block type: {block_type}",
            width=raw,
        )


def _degraded_block(reason: str, width: Any = None) -> dict[str, Any]:
    if isinstance(width, dict):
        width_class = _resolve_block_width_class(width)
    else:
        width_class = _resolve_width_class(width)
    return {
        "type": "degraded",
        "width_class": width_class,
        "reason": _safe_str(reason),
        "title": "Unavailable block",
    }


def _render_hero_snapshot(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")
    if "links" in raw:
        _require_list(raw, "links")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = validate_internal_href(item.get("href"))
        items.append(
            {
                "label": _safe_str(item.get("label")),
                "value": _safe_str(item.get("value")),
                "href": href,
            }
        )

    links: list[dict[str, Any]] = []
    for link in _safe_dict_list(raw.get("links")):
        href = validate_internal_href(link.get("href"))
        if href is not None:
            links.append(
                {
                    "label": _safe_str(link.get("label")),
                    "href": href,
                }
            )

    return {
        "type": "hero_snapshot",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "subtitle": _safe_str(raw.get("subtitle")),
        "status": _safe_str(raw.get("status")),
        "items": items,
        "links": links,
    }


def _render_metric_card(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_scalar(raw, "value")

    return {
        "type": "metric_card",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "value": _safe_str(raw.get("value", "n/a")),
        "status": _safe_str(raw.get("status", "")),
        "hint": _safe_str(raw.get("hint", "")),
    }


def _render_kpi_strip(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        items.append(
            {
                "label": _safe_str(item.get("label")),
                "value": _safe_str(item.get("value")),
                "status": _safe_str(item.get("status", "")),
            }
        )
    return {
        "type": "kpi_strip",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "items": items,
    }


def _render_venue_summary_grid(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        items.append(
            {
                "label": _safe_str(item.get("label")),
                "value": _safe_str(item.get("value")),
                "status": _safe_str(item.get("status", "")),
            }
        )
    return {
        "type": "venue_summary_grid",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "items": items,
    }


def _render_mode_cards(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = validate_internal_href(item.get("href"))
        latest_href = validate_internal_href(item.get("latest_href"))
        items.append(
            {
                "label": _display_value(item.get("label")),
                "value": _display_value(item.get("value")),
                "status": _safe_str(item.get("status", "")),
                "href": href,
                "latest": _display_value(item.get("latest")),
                "latest_href": latest_href,
            }
        )
    return {
        "type": "mode_cards",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "items": items,
    }


def _render_status_table(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    columns = _safe_columns(raw.get("columns"))
    rows = _safe_table_rows(raw.get("rows"), len(columns))

    return {
        "type": "status_table",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "columns": columns,
        "rows": rows,
    }


def _render_event_table(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    columns = _safe_columns(raw.get("columns"))
    rows = _safe_table_rows(raw.get("rows"), len(columns))

    return {
        "type": "event_table",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "columns": columns,
        "rows": rows,
    }


def _render_attention_list(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        items.append(
            {
                "label": _display_value(item.get("label")),
                "message": _display_value(item.get("message")),
                "severity": _safe_str(item.get("severity", "warning")),
            }
        )
    return {
        "type": "attention_list",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "items": items,
    }


def _render_artifact_links(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = validate_internal_href(item.get("href"))
        items.append(
            {
                "label": _safe_str(item.get("label")),
                "href": href,
                "content_type": _safe_str(item.get("content_type", "")),
            }
        )
    return {
        "type": "artifact_links",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "items": items,
    }


def _render_raw_json_panel(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    return {
        "type": "raw_json_panel",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "data": raw.get("data"),
    }


_ALLOWED_CHART_KINDS: frozenset = frozenset({"line", "bar", "area", "donut"})


def _render_chart(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    raw_kind = raw.get("kind")
    kind = raw_kind if raw_kind in _ALLOWED_CHART_KINDS else None
    series, state = _normalize_chart_series(kind, raw.get("series"))
    labels = _normalize_chart_display_values(raw.get("labels"))
    categories = _normalize_chart_display_values(raw.get("categories"))

    if raw_kind is not None and kind is None:
        state = "degraded"
    has_data = state == "ready"

    height = raw.get("height")
    if not isinstance(height, int) or height < 50 or height > 800:
        height = 300

    resolved_kind = kind or "line"
    chart_config: dict[str, Any] = {
        "chart": {
            "type": resolved_kind,
            "height": height,
            "toolbar": {"show": False},
            "zoom": {"enabled": False},
            "background": "transparent",
        },
        "series": series,
        "dataLabels": {"enabled": False},
        "stroke": {"curve": "smooth", "width": 2},
        "theme": {"mode": "light"},
        "grid": {
            "borderColor": "transparent",
            "row": {"colors": ["transparent", "transparent"]},
        },
        "yaxis": {
            "labels": {
                "style": {"colors": "var(--beeui-text-secondary)", "fontSize": "11px"},
            },
        },
        "legend": {
            "show": True,
            "position": "bottom",
            "fontSize": "12px",
            "labels": {"colors": "var(--beeui-text-secondary)"},
            "markers": {"width": 8, "height": 8, "radius": 4},
        },
    }
    if resolved_kind == "donut":
        chart_config["labels"] = labels
        chart_config["plotOptions"] = {"pie": {"donut": {"size": "65%"}}}
    else:
        xaxis: dict[str, Any] = {
            "labels": {
                "style": {"colors": "var(--beeui-text-muted)", "fontSize": "11px"},
            },
        }
        if categories:
            xaxis["categories"] = categories
        chart_config["xaxis"] = xaxis

    colors = _normalize_chart_colors(raw.get("colors"))
    if colors:
        chart_config["colors"] = colors

    horizontal = (
        raw.get("horizontal") if isinstance(raw.get("horizontal"), bool) else False
    )
    if resolved_kind == "bar" and not horizontal:
        chart_config.setdefault("plotOptions", {})
        chart_config["plotOptions"]["bar"] = {
            "borderRadius": 4,
            "columnWidth": "55%",
        }
        chart_config["dataLabels"] = {
            "enabled": True,
            "offsetY": -4,
            "style": {"fontSize": "11px", "colors": ["var(--beeui-text-muted)"]},
        }
        chart_config["grid"] = {
            "xaxis": {"lines": {"show": False}},
            "yaxis": {"lines": {"show": True}},
        }

    if resolved_kind == "bar" and horizontal:
        chart_config.setdefault("plotOptions", {})
        bar_height = raw.get("barHeight", "50%")
        if not isinstance(bar_height, str) or not _BAR_HEIGHT_PATTERN.fullmatch(
            bar_height
        ):
            bar_height = "50%"
        chart_config["plotOptions"]["bar"] = {
            "horizontal": True,
            "barHeight": bar_height,
        }
        # Clean list-like appearance: hide axis lines, show data labels on bars
        chart_config["xaxis"] = {
            "labels": {"show": False},
            "axisBorder": {"show": False},
            "axisTicks": {"show": False},
        }
        chart_config.pop("yaxis", None)
        chart_config["grid"] = {
            "xaxis": {"lines": {"show": False}},
            "yaxis": {"lines": {"show": False}},
        }
        chart_config["dataLabels"] = {
            "enabled": True,
            "offsetX": 4,
            "style": {"fontSize": "12px", "colors": ["var(--beeui-text-secondary)"]},
        }

    if resolved_kind == "area":
        chart_config["fill"] = {
            "type": "gradient",
            "gradient": {
                "shadeIntensity": 1,
                "opacityFrom": 0.45,
                "opacityTo": 0.05,
            },
        }

    title = _safe_str(raw.get("title", ""))
    chart_id = _normalize_chart_id(raw.get("chart_id"), title, chart_config)

    return {
        "type": "chart",
        "width_class": width_class,
        "title": title,
        "subtitle": _safe_str(raw.get("subtitle", "")),
        "status": _safe_str(raw.get("status", "")),
        "hint": _safe_str(raw.get("hint", "")),
        "kind": resolved_kind,
        "series": series,
        "labels": labels,
        "categories": categories,
        "height": height,
        "unit": _safe_str(raw.get("unit", "")),
        "empty_message": _safe_str(raw.get("empty_message", "No chart data")),
        "has_data": has_data,
        "state": state,
        "chart_id": chart_id,
        "chart_config": chart_config,
    }


def _chart_id_from_config(title: str, chart_config: dict[str, Any]) -> str:
    payload = json.dumps(
        {"title": title, "config": chart_config},
        ensure_ascii=True,
        sort_keys=True,
        default=str,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"beeui-chart-{digest}"


def _render_operator_hero(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = validate_internal_href(item.get("href"))
        normalized_item: dict[str, Any] = {
            "label": _display_value(item.get("label")),
            "value": _display_value(item.get("value")),
            "href": href,
        }
        progress = item.get("progress")
        if (
            isinstance(progress, (int, float))
            and not isinstance(progress, bool)
            and math.isfinite(progress)
        ):
            normalized_item["progress"] = min(100, max(0, progress))
            progress_tone = item.get("progress_tone")
            normalized_item["progress_tone"] = (
                progress_tone
                if isinstance(progress_tone, str) and progress_tone in _PROGRESS_TONES
                else "bg-primary"
            )
        items.append(normalized_item)

    primary_links: list[dict[str, Any]] = []
    for link in _safe_dict_list(raw.get("primary_links")):
        href = validate_internal_href(link.get("href"))
        if href is not None:
            normalized_link: dict[str, Any] = {
                "label": _display_value(link.get("label")),
                "href": href,
            }
            period = _safe_str(link.get("period", ""))
            if period:
                normalized_link["period"] = period
                normalized_link["active"] = bool(link.get("active", False))
            else:
                normalized_link["period"] = ""
                normalized_link["active"] = False
            primary_links.append(normalized_link)

    return {
        "type": "operator_hero",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "subtitle": _display_value(raw.get("subtitle")),
        "status": _safe_str(raw.get("status", "")),
        "items": items,
        "primary_links": primary_links,
    }


def _render_venue_card(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        items.append(
            {
                "label": _display_value(item.get("label")),
                "value": _display_value(item.get("value")),
                "status": _safe_str(item.get("status", "")),
            }
        )

    alerts: list[dict[str, str]] = []
    for alert in _safe_dict_list(raw.get("alerts")):
        alerts.append(
            {
                "severity": _safe_str(alert.get("severity", "warning")),
                "message": _display_value(alert.get("message")),
            }
        )

    links: list[dict[str, Any]] = []
    for link in _safe_dict_list(raw.get("links")):
        href = validate_internal_href(link.get("href"))
        if href is not None:
            links.append(
                {
                    "label": _display_value(link.get("label")),
                    "href": href,
                }
            )

    return {
        "type": "venue_card",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "subtitle": _display_value(raw.get("subtitle")),
        "status": _safe_str(raw.get("status", "")),
        "compact": bool(raw.get("compact", False)),
        "items": items,
        "alerts": alerts,
        "links": links,
    }


def _render_kpi_grid(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    columns = resolve_kpi_grid_columns(raw.get("columns"))
    column_classes = _KPI_GRID_COLUMN_CLASSES[columns]

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        items.append(
            {
                "label": _display_value(item.get("label")),
                "value": _display_value(item.get("value")),
                "unit": _display_value(item.get("unit"), default=""),
                "status": _safe_str(item.get("status", "")),
                "hint": _display_value(item.get("hint"), default=""),
            }
        )
    return {
        "type": "kpi_grid",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "columns": columns,
        "column_classes": column_classes,
        "items": items,
    }


def _render_group(
    raw: dict[str, Any],
    width_class: str,
    *,
    depth: int = _GROUP_MAX_DEPTH,
) -> dict[str, Any]:
    if depth <= 0:
        return _degraded_block("Group nesting depth exceeded", width=raw)

    direction = raw.get("direction", "vertical")
    if not isinstance(direction, str) or direction not in ("vertical",):
        direction = "vertical"

    children_raw = raw.get("children")
    if not isinstance(children_raw, list):
        return _degraded_block("Group children are missing or invalid", width=raw)

    children = [_render_block(child, depth=depth - 1) for child in children_raw]

    return {
        "type": "group",
        "width_class": width_class,
        "direction": direction,
        "children": children,
    }


def _render_state_grid(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        items.append(
            {
                "label": _display_value(item.get("label")),
                "value": _display_value(item.get("value")),
                "status": _safe_str(item.get("status", "")),
            }
        )
    return {
        "type": "state_grid",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "items": items,
    }


def _render_quick_links(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = validate_internal_href(item.get("href"))
        items.append(
            {
                "label": _display_value(item.get("label")),
                "href": href,
            }
        )
    return {
        "type": "quick_links",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "items": items,
    }


def _render_run_table(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    columns = _safe_run_table_columns(raw.get("columns"))
    raw_rows = _safe_dict_list(raw.get("rows"))

    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        run_href = validate_internal_href(row.get("run_href"))
        artifact_href = validate_internal_href(row.get("artifact_href"))
        rows.append(
            {
                "run_id": _display_value(row.get("run_id")),
                "run_href": run_href,
                "mode": _display_value(row.get("mode")),
                "venue": _display_value(row.get("venue")),
                "symbol": _display_value(row.get("symbol")),
                "timeframe": _display_value(row.get("timeframe")),
                "started_utc": _display_value(row.get("started_utc")),
                "health": _display_value(row.get("health")),
                "event_time_utc": _display_value(row.get("event_time_utc")),
                "event": _display_value(row.get("event")),
                "severity": _display_value(row.get("severity")),
                "events": _display_value(row.get("events")),
                "artifact": _display_value(row.get("artifact")),
                "artifact_href": artifact_href,
            }
        )

    filters = bool(raw.get("filters", False))

    return {
        "type": "run_table",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "columns": columns,
        "rows": rows,
        "filters": filters,
    }


_ALLOWED_DATA_TABLE_CELL_TYPES: frozenset = frozenset(
    {"text", "muted", "link", "badge", "status", "avatar_text", "progress", "actions"}
)
_ALLOWED_DATA_TABLE_TONES: frozenset[str] = frozenset(
    {
        "primary",
        "secondary",
        "success",
        "warning",
        "danger",
        "info",
        "blue",
        "azure",
        "indigo",
        "purple",
        "pink",
        "red",
        "orange",
        "yellow",
        "lime",
        "green",
        "teal",
        "cyan",
    }
)
_ALLOWED_DATA_TABLE_STATUSES: frozenset[str] = frozenset(
    {
        "ok",
        "warning",
        "error",
        "unknown",
        "partial",
        "degraded",
        "unavailable",
        "disabled",
        "success",
        "danger",
        "info",
    }
)
_ALLOWED_DATA_TABLE_COLORS: frozenset[str] = frozenset(
    {
        "primary",
        "secondary",
        "success",
        "warning",
        "danger",
        "info",
        "blue",
        "azure",
        "indigo",
        "purple",
        "pink",
        "red",
        "orange",
        "yellow",
        "lime",
        "green",
        "teal",
        "cyan",
    }
)


def _safe_visual_token(
    value: Any,
    allowed: frozenset[str],
    default: str = "",
) -> str:
    if not isinstance(value, str):
        return default

    clean = value.strip().lower()
    if clean in allowed:
        return clean

    return default


def _render_data_table(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    variant = raw.get("variant", "card")
    if not isinstance(variant, str) or variant not in ("card",):
        variant = "card"

    striped = bool(raw.get("striped", False))
    mobile = raw.get("mobile")
    if not isinstance(mobile, str) or mobile not in ("sm", "md", "lg"):
        mobile = None

    selectable = bool(raw.get("selectable", False))
    nowrap = bool(raw.get("nowrap", False))
    compact = bool(raw.get("compact", False))

    toolbar_raw = raw.get("toolbar")
    toolbar: dict[str, Any] = {
        "search": False,
        "entries": False,
        "actions": [],
        "fields": [],
        "hidden": {},
        "column_toggles": [],
        "has_date_range": False,
    }
    if isinstance(toolbar_raw, dict):
        toolbar["search"] = bool(toolbar_raw.get("search", False))
        toolbar["entries"] = bool(toolbar_raw.get("entries", False))
        actions: list[dict[str, Any]] = []
        for action in _safe_dict_list(toolbar_raw.get("actions")):
            href = validate_internal_href(action.get("href"))
            if href is not None:
                actions.append(
                    {
                        "label": _display_value(action.get("label")),
                        "href": href,
                    }
                )
                continue
            bounded = _normalize_table_action(action)
            if bounded is not None:
                actions.append(bounded)
        toolbar["actions"] = actions
        toolbar["fields"] = _normalize_filter_fields(toolbar_raw.get("fields", []))
        toolbar["hidden"] = _normalize_filter_hidden(toolbar_raw.get("hidden", {}))
        toolbar["column_toggles"] = _normalize_column_toggles(
            toolbar_raw.get("column_toggles", [])
        )
        toolbar["has_date_range"] = any(
            isinstance(f, dict) and f.get("type") == "date_range"
            for f in toolbar["fields"]
        )
        for action_key in ("apply", "reset"):
            action_raw = toolbar_raw.get(action_key)
            if isinstance(action_raw, dict):
                a: dict[str, Any] = {
                    "label": _safe_str(action_raw.get("label", action_key)),
                }
                href_raw = action_raw.get("href")
                if isinstance(href_raw, str) and href_raw:
                    validated_href = validate_internal_href(href_raw)
                    if validated_href is not None:
                        a["href"] = validated_href
                toolbar[action_key] = a

    columns_raw = raw.get("columns")
    degraded_error: str | None = None
    if not isinstance(columns_raw, list) or not columns_raw:
        degraded_error = "Data table columns are missing or invalid"
        columns_raw = []

    columns: list[dict[str, Any]] = []
    for col in columns_raw or []:
        if not isinstance(col, dict):
            degraded_error = (
                degraded_error or "Data table columns are missing or invalid"
            )
            continue
        key = _safe_str(col.get("key", ""))
        if not key:
            degraded_error = (
                degraded_error or "Data table column key is missing or invalid"
            )
            continue
        cell_type = col.get("cell", "text")
        if (
            not isinstance(cell_type, str)
            or cell_type not in _ALLOWED_DATA_TABLE_CELL_TYPES
        ):
            cell_type = "text"
        sortable = bool(col.get("sortable", False))
        sort_href_raw = col.get("sort_href")
        sort_href = (
            validate_internal_href(sort_href_raw)
            if sortable and sort_href_raw
            else None
        )
        sort_direction_raw = col.get("sort_direction")
        sort_direction = (
            {
                "asc": "ascending",
                "ascending": "ascending",
                "desc": "descending",
                "descending": "descending",
            }.get(sort_direction_raw)
            if isinstance(sort_direction_raw, str)
            else None
        )
        sort_active = (
            bool(col.get("sort_active", False))
            and bool(sort_href)
            and sort_direction is not None
        )
        columns.append(
            {
                "key": key,
                "label": _safe_str(col.get("label", "")),
                "cell": cell_type,
                "sortable": sortable,
                "sort_href": sort_href,
                "sort_active": sort_active,
                "sort_direction": sort_direction,
            }
        )

    rows_raw = raw.get("rows")
    if not isinstance(rows_raw, list):
        degraded_error = degraded_error or "Data table rows are missing or invalid"
        rows_raw = []

    rows: list[dict[str, Any]] = []
    for row in rows_raw:
        if not isinstance(row, dict):
            continue
        parsed_row: dict[str, Any] = {}
        for col in columns:
            key = col["key"]
            cell_type = col["cell"]
            cell_raw = row.get(key)
            parsed_row[key] = _render_data_table_cell(cell_raw, cell_type)
        rows.append(parsed_row)

    table_id = raw.get("id")
    if not isinstance(table_id, str) or not _DATA_TABLE_ID_PATTERN.fullmatch(table_id):
        table_id = None

    pagination = _normalize_data_table_pagination(raw.get("pagination"))

    return {
        "type": "data_table",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "description": _display_value(raw.get("description"), default=""),
        "variant": variant,
        "striped": striped,
        "mobile": mobile,
        "selectable": selectable,
        "nowrap": nowrap,
        "compact": compact,
        "table_id": table_id,
        "toolbar": toolbar,
        "columns": columns,
        "rows": rows,
        "pagination": pagination,
        "degraded_error": degraded_error,
    }


def _normalize_data_table_pagination(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}

    pages_by_number: dict[int, dict[str, Any]] = {}
    for index, page in enumerate(_safe_dict_list(raw.get("pages")), start=1):
        href = validate_internal_href(page.get("href"))
        number = page.get("number", page.get("label"))
        if isinstance(number, str) and number.isdecimal():
            number = int(number)
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            number = index
        if number < 1:
            continue
        if href is None or number in pages_by_number:
            continue
        pages_by_number[number] = {
            "label": _safe_str(page.get("label", number)) or str(number),
            "href": href,
            "active": bool(page.get("active", False)),
            "number": number,
        }

    pages = [pages_by_number[number] for number in sorted(pages_by_number)]
    active_index = next(
        (index for index, page in enumerate(pages) if page["active"]),
        None,
    )
    visible_pages = _compact_data_table_pages(pages, active_index)
    page_param = raw.get("page_param", "page")
    if not isinstance(page_param, str) or not _DATA_TABLE_ID_PATTERN.fullmatch(
        page_param
    ):
        page_param = "page"

    return {
        "label": _safe_str(raw.get("label", "")),
        "pages": visible_pages,
        "previous": _normalize_data_table_pagination_control(
            raw.get("previous"), pages, active_index, -1
        ),
        "next": _normalize_data_table_pagination_control(
            raw.get("next"), pages, active_index, 1
        ),
        "page_param": page_param,
        "page_size": _normalize_data_table_page_size(raw.get("page_size")),
    }


def _compact_data_table_pages(
    pages: list[dict[str, Any]], active_index: int | None
) -> list[dict[str, Any]]:
    if len(pages) <= 6:
        return pages

    current_index = active_index if active_index is not None else 0
    selected = {0, len(pages) - 1}
    selected.update(
        index
        for index in range(current_index - 1, current_index + 2)
        if 0 <= index < len(pages)
    )
    compact: list[dict[str, Any]] = []
    previous_index: int | None = None
    for index in sorted(selected):
        if previous_index is not None and index > previous_index + 1:
            compact.append({"ellipsis": True})
        compact.append(pages[index])
        previous_index = index
    return compact


def _normalize_data_table_pagination_control(
    raw: Any,
    pages: list[dict[str, Any]],
    active_index: int | None,
    offset: int,
) -> dict[str, str] | None:
    if isinstance(raw, dict):
        href = validate_internal_href(raw.get("href"))
        if href is not None:
            return {"label": _safe_str(raw.get("label", "")), "href": href}
    if active_index is None:
        return None
    index = active_index + offset
    if 0 <= index < len(pages):
        return {"label": "", "href": pages[index]["href"]}
    return None


def _normalize_data_table_page_size(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    options: list[dict[str, Any]] = []
    for option in _safe_dict_list(raw.get("options"))[:20]:
        href = validate_internal_href(option.get("href"))
        if href is None:
            continue
        value = _safe_str(option.get("value", option.get("label", "")))
        label = _safe_str(option.get("label", value))
        if not value or not label:
            continue
        options.append(
            {
                "value": value,
                "label": label,
                "href": href,
                "active": bool(option.get("active", False)),
            }
        )
    if not options:
        return None
    current = _safe_str(raw.get("current", ""))
    return {
        "label": _safe_str(raw.get("label", "")),
        "current": current,
        "options": options,
    }


def _render_data_table_cell(cell_raw: Any, cell_type: str) -> dict[str, Any]:
    if cell_type == "actions":
        actions: list[dict[str, Any]] = []
        for action in _safe_dict_list(
            cell_raw
            if isinstance(cell_raw, list)
            else cell_raw.get("items", [])
            if isinstance(cell_raw, dict)
            else []
        ):
            href = validate_internal_href(action.get("href"))
            if href is not None:
                actions.append(
                    {
                        "label": _display_value(action.get("label")),
                        "href": href,
                    }
                )
                continue
            bounded = _normalize_table_action(action)
            if bounded is not None:
                actions.append(bounded)
        return {"type": "actions", "items": actions}


    if not isinstance(cell_raw, dict):
        return {"type": "text", "value": _display_value(cell_raw)}

    if cell_type == "link":
        href = validate_internal_href(cell_raw.get("href"))
        return {
            "type": "link",
            "label": _display_value(cell_raw.get("label")),
            "href": href,
        }

    if cell_type == "badge":
        return {
            "type": "badge",
            "label": _display_value(cell_raw.get("label")),
            "tone": _safe_visual_token(
                cell_raw.get("tone"),
                _ALLOWED_DATA_TABLE_TONES,
                "secondary",
            ),
        }

    if cell_type == "status":
        return {
            "type": "status",
            "label": _display_value(cell_raw.get("label")),
            "status": _safe_visual_token(
                cell_raw.get("status"),
                _ALLOWED_DATA_TABLE_STATUSES,
                "unknown",
            ),
        }

    if cell_type == "avatar_text":
        return {
            "type": "avatar_text",
            "title": _display_value(cell_raw.get("title")),
            "subtitle": _display_value(cell_raw.get("subtitle"), default=""),
            "initials": _safe_str(cell_raw.get("initials", "")),
            "color": _safe_visual_token(
                cell_raw.get("color"),
                _ALLOWED_DATA_TABLE_COLORS,
            ),
        }

    if cell_type == "progress":
        value = cell_raw.get("value")
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            value = 0
        value = max(value, 0)
        value = min(value, 100)
        return {
            "type": "progress",
            "label": _display_value(cell_raw.get("label")),
            "value": value,
            "color": _safe_visual_token(
                cell_raw.get("color"),
                _ALLOWED_DATA_TABLE_COLORS,
            ),
        }

    tone = "muted" if cell_type == "muted" else ""
    return {
        "type": "text",
        "value": _display_value(
            cell_raw.get("label") if isinstance(cell_raw, dict) else cell_raw
        ),
        "tone": tone,
    }


def _normalize_table_action(raw: dict[str, Any]) -> dict[str, Any] | None:
    action_id = raw.get("action_id")
    if not isinstance(action_id, str) or not _DATA_TABLE_ID_PATTERN.fullmatch(action_id):
        return None
    label = _display_value(raw.get("label"), default="")
    if not label or len(label) > 256:
        return None
    description = _display_value(raw.get("description"), default="")
    if len(description) > 512:
        return None
    confirmation = _display_value(raw.get("confirmation"), default="")
    if len(confirmation) > 512:
        return None
    flow = raw.get("flow", "preview_confirm_execute")
    if flow not in {"preview_confirm_execute", "direct_execute"}:
        return None
    icon = raw.get("icon", "")
    if icon not in {"", "edit", "trash", "device-floppy", "x"}:
        return None
    inline_edit = raw.get("inline_edit", False)
    if not isinstance(inline_edit, bool):
        return None
    if inline_edit and (flow != "direct_execute" or not icon):
        return None
    args_raw = raw.get("args", {})
    if not isinstance(args_raw, dict) or len(args_raw) > 10:
        return None
    args: dict[str, str] = {}
    for key, value in args_raw.items():
        if not isinstance(key, str) or not _DATA_TABLE_ID_PATTERN.fullmatch(key):
            return None
        if not isinstance(value, str) or len(value) > 256:
            return None
        args[key] = value
    fields_raw = raw.get("fields", [])
    if not isinstance(fields_raw, list) or len(fields_raw) > 10:
        return None
    fields: list[dict[str, Any]] = []
    for field in _safe_dict_list(fields_raw):
        name = field.get("name")
        field_type = field.get("type")
        if (
            not isinstance(name, str)
            or not _DATA_TABLE_ID_PATTERN.fullmatch(name)
            or field_type not in {"text", "email"}
        ):
            return None
        max_length = field.get("max_length", 254)
        if not isinstance(max_length, int) or isinstance(max_length, bool):
            return None
        value = field.get("value", field.get("initial", ""))
        if not isinstance(value, str) or len(value) > min(max(max_length, 1), 254):
            return None
        field_label = _display_value(field.get("label"), default=name)
        if len(field_label) > 256:
            return None
        fields.append(
            {
                "name": name,
                "type": field_type,
                "label": field_label,
                "required": bool(field.get("required", True)),
                "max_length": min(max(max_length, 1), 254),
                "value": value,
            }
        )
    return {
        "action_id": action_id,
        "label": label,
        "description": description,
        "confirmation": confirmation,
        "flow": flow,
        "icon": icon,
        "inline_edit": inline_edit,
        "args": args,
        "fields": fields,
    }


def _normalize_filter_fields(fields_raw: Any) -> list[dict[str, Any]]:
    if not isinstance(fields_raw, list):
        return []

    fields: list[dict[str, Any]] = []
    for field in fields_raw:
        if not isinstance(field, dict):
            continue
        ft = _safe_str(field.get("type"))
        name = _safe_str(field.get("name"))
        label = _safe_str(field.get("label", name))
        value = field.get("value", "")
        if not isinstance(value, str):
            value = str(value) if value is not None else ""

        entry: dict[str, Any] = {
            "type": ft,
            "name": name,
            "label": label,
            "value": value,
        }

        if ft == "date_range":
            entry["from_value"] = _safe_str(field.get("from_value", ""))
            entry["to_value"] = _safe_str(field.get("to_value", ""))
            entry["from_label"] = _safe_str(field.get("from_label", "From"))
            entry["to_label"] = _safe_str(field.get("to_label", "To"))

        if ft in ("text",):
            entry["placeholder"] = _safe_str(field.get("placeholder", ""))

        if ft == "select":
            options_raw = field.get("options", [])
            if not isinstance(options_raw, list):
                options_raw = []
            entry["options"] = [
                {
                    "value": _safe_str(o.get("value")) if isinstance(o, dict) else "",
                    "label": _safe_str(o.get("label"))
                    if isinstance(o, dict)
                    else _safe_str(o),
                }
                for o in options_raw
                if isinstance(o, dict) and o.get("value")
            ]
            entry["multi"] = bool(field.get("multi", False))
            entry["placeholder"] = _safe_str(field.get("placeholder", ""))

        if ft == "checkboxes":
            choices_raw = field.get("choices", [])
            entry["choices"] = []
            if isinstance(choices_raw, list):
                for ch in choices_raw:
                    if not isinstance(ch, dict):
                        continue
                    val = _safe_str(ch.get("value", ""))
                    lbl = _safe_str(ch.get("label", val))
                    checked = bool(ch.get("checked", False))
                    toggle_href_raw = ch.get("toggle_href", "")
                    toggle_href = (
                        validate_internal_href(toggle_href_raw)
                        if toggle_href_raw
                        else None
                    )
                    entry["choices"].append(
                        {
                            "value": val,
                            "label": lbl,
                            "checked": checked,
                            "toggle_href": toggle_href,
                        }
                    )
            entry["open"] = bool(field.get("open", False))
            raw_count = field.get("selected_count", 0)
            if isinstance(raw_count, (int, float)) and not isinstance(raw_count, bool):
                entry["selected_count"] = int(raw_count)
            else:
                entry["selected_count"] = 0

        fields.append(entry)

    return fields


def _normalize_filter_hidden(hidden_raw: Any) -> dict[str, str]:
    hidden: dict[str, str] = {}
    if isinstance(hidden_raw, dict):
        for hk, hv in hidden_raw.items():
            if isinstance(hk, str) and isinstance(hv, str):
                hidden[hk] = hv
    return hidden


def _normalize_column_toggles(toggles_raw: Any) -> list[dict[str, Any]]:
    toggles: list[dict[str, Any]] = []
    if isinstance(toggles_raw, list):
        for ct in toggles_raw:
            if isinstance(ct, dict):
                key = _safe_str(ct.get("key", ""))
                label = _safe_str(ct.get("label", key))
                visible = bool(ct.get("visible", False))
                toggle_href_raw = ct.get("toggle_href", "")
                toggle_href = (
                    validate_internal_href(toggle_href_raw) if toggle_href_raw else None
                )
                toggles.append(
                    {
                        "key": key,
                        "label": label,
                        "visible": visible,
                        "toggle_href": toggle_href,
                    }
                )
    return toggles


def _normalize_filter_actions(actions_raw: Any) -> dict[str, Any]:
    actions: dict[str, Any] = {}
    if not isinstance(actions_raw, dict):
        return actions
    for action_key in ("apply", "reset"):
        action_raw = actions_raw.get(action_key)
        if isinstance(action_raw, dict):
            a: dict[str, Any] = {
                "label": _safe_str(action_raw.get("label", action_key)),
            }
            href_raw = action_raw.get("href")
            if isinstance(href_raw, str) and href_raw:
                validated_href = validate_internal_href(href_raw)
                if validated_href is not None:
                    a["href"] = validated_href
            actions[action_key] = a
    return actions


def _render_filter_form(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    title = _safe_str(raw.get("title", "Filters"))

    fields = _normalize_filter_fields(raw.get("fields", []))
    hidden = _normalize_filter_hidden(raw.get("hidden", {}))
    column_toggles = _normalize_column_toggles(raw.get("column_toggles", []))
    actions = _normalize_filter_actions(raw.get("actions", {}))

    columns_open = bool(raw.get("columns_open", False))
    columns_toggle_href_raw = raw.get("columns_toggle_href", "")
    columns_toggle_href = (
        validate_internal_href(columns_toggle_href_raw)
        if columns_toggle_href_raw
        else None
    )

    return {
        "type": "filter_form",
        "width_class": width_class,
        "title": title,
        "hidden": hidden,
        "fields": fields,
        "has_date_range": any(field.get("type") == "date_range" for field in fields),
        "column_toggles": column_toggles,
        "columns_open": columns_open,
        "columns_toggle_href": columns_toggle_href,
        "actions": actions,
    }


_BLOCK_RENDERERS: dict[str, Any] = {
    "hero_snapshot": _render_hero_snapshot,
    "metric_card": _render_metric_card,
    "kpi_strip": _render_kpi_strip,
    "venue_summary_grid": _render_venue_summary_grid,
    "mode_cards": _render_mode_cards,
    "status_table": _render_status_table,
    "event_table": _render_event_table,
    "attention_list": _render_attention_list,
    "artifact_links": _render_artifact_links,
    "raw_json_panel": _render_raw_json_panel,
    "chart": _render_chart,
    "operator_hero": _render_operator_hero,
    "venue_card": _render_venue_card,
    "kpi_grid": _render_kpi_grid,
    "state_grid": _render_state_grid,
    "quick_links": _render_quick_links,
    "run_table": _render_run_table,
    "group": _render_group,
    "data_table": _render_data_table,
    "filter_form": _render_filter_form,
}


def render_layout(layout: Any) -> list[dict[str, Any]]:
    if not isinstance(layout, list):
        return []
    return [_render_block(item, depth=_GROUP_MAX_DEPTH) for item in layout]


def resolve_layout_links(
    blocks: list[dict[str, Any]],
    route_prefix: str,
    current_path: str,
) -> None:
    for block in blocks:
        if block.get("type") == "group":
            children = block.get("children")
            if isinstance(children, list):
                resolve_layout_links(children, route_prefix, current_path)
            continue
        if block.get("type") == "filter_form":
            actions = block.get("actions")
            apply = actions.get("apply") if isinstance(actions, dict) else None
            apply_href = apply.get("href") if isinstance(apply, dict) else None
            block["form_action"] = prefix_internal_href(
                route_prefix,
                apply_href if isinstance(apply_href, str) else current_path,
            )
            for key in ("columns_toggle_href",):
                href = block.get(key)
                if isinstance(href, str):
                    block[key] = prefix_internal_href(route_prefix, href)
            if isinstance(actions, dict):
                reset = actions.get("reset")
                if isinstance(reset, dict) and isinstance(reset.get("href"), str):
                    reset["href"] = prefix_internal_href(route_prefix, reset["href"])
            fields = block.get("fields")
            if isinstance(fields, list):
                for field in fields:
                    if not isinstance(field, dict):
                        continue
                    choices = field.get("choices")
                    if isinstance(choices, list):
                        for choice in choices:
                            if isinstance(choice, dict) and isinstance(
                                choice.get("toggle_href"), str
                            ):
                                choice["toggle_href"] = prefix_internal_href(
                                    route_prefix, choice["toggle_href"]
                                )
            toggles = block.get("column_toggles")
            if isinstance(toggles, list):
                for toggle in toggles:
                    if isinstance(toggle, dict) and isinstance(
                        toggle.get("toggle_href"), str
                    ):
                        toggle["toggle_href"] = prefix_internal_href(
                            route_prefix, toggle["toggle_href"]
                        )
        if block.get("type") == "data_table":
            apply_href_override = None
            toolbar = block.get("toolbar")
            if isinstance(toolbar, dict):
                actions = toolbar.get("actions")
                if isinstance(actions, list):
                    for action in actions:
                        if isinstance(action, dict) and isinstance(
                            action.get("href"), str
                        ):
                            action["href"] = prefix_internal_href(
                                route_prefix, action["href"]
                            )
                for action_key in ("apply", "reset"):
                    a = toolbar.get(action_key)
                    if isinstance(a, dict) and isinstance(a.get("href"), str):
                        a["href"] = prefix_internal_href(route_prefix, a["href"])
                fields = toolbar.get("fields")
                if isinstance(fields, list):
                    for field in fields:
                        if not isinstance(field, dict):
                            continue
                        choices = field.get("choices")
                        if isinstance(choices, list):
                            for choice in choices:
                                if isinstance(choice, dict) and isinstance(
                                    choice.get("toggle_href"), str
                                ):
                                    choice["toggle_href"] = prefix_internal_href(
                                        route_prefix, choice["toggle_href"]
                                    )
                toggles = toolbar.get("column_toggles")
                if isinstance(toggles, list):
                    for toggle in toggles:
                        if isinstance(toggle, dict) and isinstance(
                            toggle.get("toggle_href"), str
                        ):
                            toggle["toggle_href"] = prefix_internal_href(
                                route_prefix, toggle["toggle_href"]
                            )
                apply = toolbar.get("apply")
                apply_href = apply.get("href") if isinstance(apply, dict) else None
                apply_href_override = (
                    apply_href if isinstance(apply_href, str) else None
                )

            columns = block.get("columns")
            if isinstance(columns, list):
                for column in columns:
                    if isinstance(column, dict) and isinstance(
                        column.get("sort_href"), str
                    ):
                        column["sort_href"] = prefix_internal_href(
                            route_prefix, column["sort_href"]
                        )

            block["form_action"] = prefix_internal_href(
                route_prefix,
                apply_href_override if apply_href_override else current_path,
            )

            pagination = block.get("pagination")
            if isinstance(pagination, dict):
                pages = pagination.get("pages")
                if isinstance(pages, list):
                    for page in pages:
                        if isinstance(page, dict) and isinstance(page.get("href"), str):
                            page["href"] = prefix_internal_href(
                                route_prefix, page["href"]
                            )
                for key in ("previous", "next"):
                    control = pagination.get(key)
                    if isinstance(control, dict) and isinstance(
                        control.get("href"), str
                    ):
                        control["href"] = prefix_internal_href(
                            route_prefix, control["href"]
                        )
                page_size = pagination.get("page_size")
                if isinstance(page_size, dict):
                    options = page_size.get("options")
                    if isinstance(options, list):
                        for option in options:
                            if isinstance(option, dict) and isinstance(
                                option.get("href"), str
                            ):
                                option["href"] = prefix_internal_href(
                                    route_prefix, option["href"]
                                )
            rows = block.get("rows")
            if isinstance(rows, list):
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    for cell in row.values():
                        if not isinstance(cell, dict):
                            continue
                        if isinstance(cell.get("href"), str):
                            cell["href"] = prefix_internal_href(
                                route_prefix, cell["href"]
                            )
                        cell_actions = cell.get("items")
                        if isinstance(cell_actions, list):
                            for action in cell_actions:
                                if isinstance(action, dict) and isinstance(
                                    action.get("href"), str
                                ):
                                    action["href"] = prefix_internal_href(
                                        route_prefix, action["href"]
                                    )


def layout_has_charts(blocks: list[dict[str, Any]]) -> bool:
    for block in blocks:
        if block.get("type") == "chart":
            return True

        children = block.get("children")
        if isinstance(children, list) and layout_has_charts(
            [child for child in children if isinstance(child, dict)]
        ):
            return True

    return False


def layout_has_date_ranges(blocks: list[dict[str, Any]]) -> bool:
    for block in blocks:
        if block.get("type") == "filter_form":
            fields = block.get("fields")
            if isinstance(fields, list):
                for field in fields:
                    if isinstance(field, dict) and field.get("type") == "date_range":
                        return True

        if block.get("type") == "data_table":
            toolbar = block.get("toolbar")
            if isinstance(toolbar, dict):
                fields = toolbar.get("fields")
                if isinstance(fields, list):
                    for field in fields:
                        if (
                            isinstance(field, dict)
                            and field.get("type") == "date_range"
                        ):
                            return True

        children = block.get("children")
        if isinstance(children, list) and layout_has_date_ranges(
            [child for child in children if isinstance(child, dict)]
        ):
            return True

    return False
