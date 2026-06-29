from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

PreviewType = Literal["json", "jsonl", "text", "unsupported"]


@dataclass(frozen=True)
class ArtifactRef:
    artifact_id: str
    content_type: str


@dataclass(frozen=True)
class ArtifactPreview:
    artifact_id: str
    content_type: str
    preview_type: PreviewType
    preview_data: Any = None
    truncated: bool = False
    row_count: int | None = None
    row_warnings: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None
    metadata_only: bool = False
