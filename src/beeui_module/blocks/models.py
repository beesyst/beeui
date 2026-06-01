from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ALLOWED_BLOCK_TYPES = {
    "metric_card",
    "kpi_grid",
    "status_card",
    "table_card",
    "links_card",
    "alert_card",
    "text_card",
    "progress_card",
}

ALLOWED_BLOCK_STATES = {"normal", "empty", "degraded", "error"}


# Размещение блока на странице с Bootstrap-подобной шириной 1..12
@dataclass(frozen=True)
class BlockPlacement:
    block_id: str
    width: int


# Валидированное описание блока из schema.yml
@dataclass(frozen=True)
class BlockDefinition:
    block_id: str
    block_type: str
    title: str
    state: str
    payload: dict[str, Any]


# Данные, подготовленные registry для конкретного Jinja template
@dataclass(frozen=True)
class RenderedBlock:
    block_id: str
    block_type: str
    title: str
    state: str
    width: int
    template_name: str
    payload: dict[str, Any]
