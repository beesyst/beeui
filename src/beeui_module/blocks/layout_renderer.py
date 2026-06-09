from __future__ import annotations

from typing import Any
from urllib.parse import unquote, urlsplit

_WIDTH_MAP: dict[int, str] = {
    12: "col-12",
    8: "col-12 col-lg-8",
    6: "col-12 col-lg-6",
    4: "col-12 col-md-6 col-lg-4",
    3: "col-12 col-sm-6 col-lg-3",
    2: "col-12 col-sm-6 col-lg-2",
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


# Определение класса ширины по целочисленному значению width
def _resolve_width_class(width: Any) -> str:
    if isinstance(width, int) and width in _WIDTH_MAP:
        return _WIDTH_MAP[width]
    return _DEFAULT_WIDTH_CLASS


# Валидация и нормализация ссылок для блоков, которые поддерживают ссылки
def _validate_link(href: Any) -> str | None:
    if not isinstance(href, str):
        return None

    value = href.strip()
    if not value or value.startswith("//"):
        return None

    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None

    if not parsed.path.startswith("/"):
        return None

    normalized_path = unquote(parsed.path).replace("\\", "/")
    if any(ord(char) < 32 for char in normalized_path):
        return None

    if any(part == ".." for part in normalized_path.split("/")):
        return None

    if any(ord(char) < 32 for char in value):
        return None

    return value


# Безопасное преобразование значения в строку для отображения в блоках
def _safe_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return ""


# Безопасное отображение user-visible значений: None, пустые или "null"/"none" -> default
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


# Нормализация списка
def _safe_list(raw: Any) -> list[Any]:
    if isinstance(raw, list):
        return raw
    return []


# Нормализация списка словарей
def _safe_dict_list(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


# Нормализация строковых данных для таблиц с проверкой формы строк
def _safe_table_rows(raw: Any, column_count: int) -> list[list[str]]:
    if not isinstance(raw, list):
        raise ValueError("Block rows are missing or invalid")

    rows: list[list[str]] = []
    for row in raw:
        if not isinstance(row, list) or len(row) != column_count:
            raise ValueError("Block row shape is invalid")
        rows.append([_safe_str(cell) for cell in row])
    return rows


# Нормализация списка столбцов
def _safe_columns(raw: Any) -> list[str]:
    if (
        not isinstance(raw, list)
        or not raw
        or not all(isinstance(column, str) for column in raw)
    ):
        raise ValueError("Block columns are missing or invalid")
    return list(raw)


# Валидация соответствия столбцов таблицы операторскому контракту для блока "run_table"
def _safe_run_table_columns(raw: Any) -> list[str]:
    columns = _safe_columns(raw)
    if tuple(columns) != _RUN_TABLE_COLUMNS:
        raise ValueError("Run table columns must match the operator contract")
    return columns


# Валидация наличия обязательного поля "title" и его типа для блоков, требующих заголовок
def _require_title(raw: dict[str, Any]) -> None:
    if not isinstance(raw.get("title"), str) or not raw["title"].strip():
        raise ValueError("Block title is missing or invalid")


# Валидация наличия обязательного поля "items" и его типа для блоков, требующих список элементов
def _require_list(raw: dict[str, Any], field: str) -> None:
    if not isinstance(raw.get(field), list):
        raise ValueError(f"Block {field} is missing or invalid")


# Валидация наличия обязательного скаляра (строка, число, булево) для указанных полей
def _require_scalar(raw: dict[str, Any], field: str) -> None:
    if not isinstance(raw.get(field), (str, int, float, bool)):
        raise ValueError(f"Block {field} is missing or invalid")


# Рендеринг одного блока из необработанных данных с валидацией и обработкой ошибок
def _render_block(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return _degraded_block("Block is not an object", width=None)

    block_type = raw.get("type")
    if not isinstance(block_type, str) or not block_type:
        return _degraded_block(
            "Block type is missing or invalid", width=raw.get("width")
        )

    if block_type not in _SUPPORTED_BLOCK_TYPES:
        return _degraded_block(
            f"Unsupported block type: {block_type}",
            width=raw.get("width"),
        )

    width_class = _resolve_width_class(raw.get("width"))

    try:
        renderer = _BLOCK_RENDERERS[block_type]
        return renderer(raw, width_class)
    except Exception:
        return _degraded_block(
            f"Failed to render block type: {block_type}",
            width=raw.get("width"),
        )


# Генерация "degraded" блока с сообщением об ошибке для случаев, когда рендеринг блока невозможен из-за ошибок в данных
def _degraded_block(reason: str, width: Any = None) -> dict[str, Any]:
    return {
        "type": "degraded",
        "width_class": _resolve_width_class(width),
        "reason": _safe_str(reason),
        "title": "Unavailable block",
    }


# Рендеринг конкретных типов блоков с валидацией их специфичных полей и структур данных
def _render_hero_snapshot(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")
    if "links" in raw:
        _require_list(raw, "links")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = _validate_link(item.get("href"))
        items.append(
            {
                "label": _safe_str(item.get("label")),
                "value": _safe_str(item.get("value")),
                "href": href,
            }
        )

    links: list[dict[str, Any]] = []
    for link in _safe_dict_list(raw.get("links")):
        href = _validate_link(link.get("href"))
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


# Рендеринг блока "metric_card" с валидацией наличия обязательных полей "title" и "value"
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


# Рендеринг блока "kpi_strip" с валидацией наличия обязательных полей "title" и "items"
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


# Рендеринг блока "venue_summary_grid" с валидацией наличия обязательных полей "title" и "items"
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


# Рендеринг блока "mode_cards" с валидацией наличия обязательных полей "title" и "items"
def _render_mode_cards(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = _validate_link(item.get("href"))
        latest_href = _validate_link(item.get("latest_href"))
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


# Рендеринг блоков "status_table" и "event_table" с валидацией наличия обязательных полей "title", "columns" и "rows"
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


# Рендеринг блоков "status_table" и "event_table" с валидацией наличия обязательных полей "title", "columns" и "rows"
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


# Рендеринг блока "attention_list" с валидацией наличия обязательных полей "title" и "items", а также структуры элементов списка
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


# Рендеринг блока "artifact_links" с валидацией наличия обязательных полей "title" и "items"
def _render_artifact_links(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = _validate_link(item.get("href"))
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


# Рендеринг блока "raw_json_panel" с валидацией наличия обязательного поля "title" и сохранением произвольных данных для отображения в виде JSON
def _render_raw_json_panel(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    return {
        "type": "raw_json_panel",
        "width_class": width_class,
        "title": _safe_str(raw.get("title")),
        "data": raw.get("data"),
    }


# Рендеринг блока "chart" с нормализацией adapter-provided chart payload
def _render_chart(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    series = _safe_list(raw.get("series"))
    points = _safe_list(raw.get("points"))
    candles = _safe_list(raw.get("candles"))
    has_data = bool(series or points or candles)

    return {
        "type": "chart",
        "width_class": width_class,
        "title": _safe_str(raw.get("title", "")),
        "subtitle": _safe_str(raw.get("subtitle", "")),
        "status": _safe_str(raw.get("status", "")),
        "hint": _safe_str(raw.get("hint", "")),
        "symbol": _safe_str(raw.get("symbol", "")),
        "timeframe": _safe_str(raw.get("timeframe", "")),
        "series": series,
        "points": points,
        "candles": candles,
        "has_data": has_data,
    }


# Рендеринг блока "operator_hero" — high-level system/operator snapshot
def _render_operator_hero(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = _validate_link(item.get("href"))
        items.append(
            {
                "label": _display_value(item.get("label")),
                "value": _display_value(item.get("value")),
                "href": href,
            }
        )

    primary_links: list[dict[str, str]] = []
    for link in _safe_dict_list(raw.get("primary_links")):
        href = _validate_link(link.get("href"))
        if href is not None:
            primary_links.append(
                {
                    "label": _display_value(link.get("label")),
                    "href": href,
                }
            )

    return {
        "type": "operator_hero",
        "width_class": width_class,
        "title": _display_value(raw.get("title")),
        "subtitle": _display_value(raw.get("subtitle")),
        "status": _safe_str(raw.get("status", "")),
        "items": items,
        "primary_links": primary_links,
    }


# Рендеринг блока "venue_card" — compact venue/operator summary card
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
        href = _validate_link(link.get("href"))
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
        "items": items,
        "alerts": alerts,
        "links": links,
    }


# Рендеринг блока "kpi_grid" — responsive KPI stat cards
def _render_kpi_grid(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)
    _require_list(raw, "items")

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
        "items": items,
    }


# Рендеринг блока "state_grid" — dense key/value state section
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


# Рендеринг блока "quick_links" — grouped internal operator links
def _render_quick_links(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    items: list[dict[str, Any]] = []
    for item in _safe_dict_list(raw.get("items")):
        href = _validate_link(item.get("href"))
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


# Рендеринг блока "run_table" — operator run/event/artifact table
def _render_run_table(raw: dict[str, Any], width_class: str) -> dict[str, Any]:
    _require_title(raw)

    columns = _safe_run_table_columns(raw.get("columns"))
    raw_rows = _safe_dict_list(raw.get("rows"))

    rows: list[dict[str, Any]] = []
    for row in raw_rows:
        run_href = _validate_link(row.get("run_href"))
        artifact_href = _validate_link(row.get("artifact_href"))
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


# Сопоставление типов блоков с их функциями рендеринга для динамического вызова при обработке layout[] списка
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
}


# Рендеринг layout[] списка
def render_layout(layout: Any) -> list[dict[str, Any]]:
    if not isinstance(layout, list):
        return []
    return [_render_block(item) for item in layout]
