from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SUPPORTED_DATA_SOURCE_TYPES = {"demo", "static"}
ALLOWED_STATIC_SOURCE_FORMATS = {"yaml", "json"}
ALLOWED_RESOLVER_STATUSES = {"ok", "partial", "error"}


@dataclass(frozen=True)
class ResolverWarning:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class DataSourceDefinition:
    source_id: str
    source_type: str
    format: str | None = None
    path: str | None = None
    root_dir: Path | None = None

    def source_ref(self) -> dict[str, str]:
        return {"type": self.source_type, "id": self.source_id}


@dataclass(frozen=True)
class ResolverEnvelope:
    status: str
    data: Any
    warnings: tuple[ResolverWarning, ...] = field(default_factory=tuple)
    source: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "source": dict(self.source),
        }


def build_envelope(
    *,
    status: str,
    data: Any,
    source: dict[str, str],
    warnings: list[ResolverWarning] | tuple[ResolverWarning, ...] | None = None,
) -> ResolverEnvelope:
    if status not in ALLOWED_RESOLVER_STATUSES:
        raise ValueError(
            f"resolver status must be one of {sorted(ALLOWED_RESOLVER_STATUSES)}"
        )

    return ResolverEnvelope(
        status=status,
        data=data,
        warnings=tuple(warnings or ()),
        source=source,
    )
