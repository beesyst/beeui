from __future__ import annotations

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class BlockPlacement:
    block_id: str
    width: int = 12
    span: int | None = None
    size: str | None = None


@dataclass(frozen=True)
class BlockDefinition:
    block_id: str
    block_type: str
    title: str
    state: str
    payload: dict[str, Any]
    source_id: str | None = None
    bindings: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderedBlock:
    block_id: str
    block_type: str
    title: str
    state: str
    width: int
    template_name: str
    payload: dict[str, Any]
