from __future__ import annotations

import copy
import json
from pathlib import Path

import yaml

from beeui_module.data.models import (
    DataSourceDefinition,
    ResolverWarning,
    build_envelope,
)

_DEMO_SOURCE_PAYLOAD = {
    "dashboard": {
        "latest_run": {"id": "run_demo_001", "status": "ok"},
        "runtime": {"status": "ok", "value": "Ready"},
        "summary": {"text": "BeeUI renders reusable schema blocks with safe escaping."},
        "kpis": {"total_runs": 24, "failed": 1},
        "kpi_items": [
            {"label": "Total runs", "value": 24, "status": "ok"},
            {"label": "Failed", "value": 1, "status": "warning"},
        ],
    },
    "runs": [
        {"id": "run_demo_001", "status": "ok"},
        {"id": "run_demo_002", "status": "partial"},
    ],
}


def load_source_data(source: DataSourceDefinition):
    if source.source_type == "demo":
        return build_envelope(
            status="ok",
            data=copy.deepcopy(_DEMO_SOURCE_PAYLOAD),
            warnings=[],
            source=source.source_ref(),
        )

    if source.source_type == "static":
        return _load_static_source(source)

    return build_envelope(
        status="error",
        data=None,
        warnings=[
            ResolverWarning(
                code="source_unsupported",
                message=f"Unsupported source type: {source.source_type}",
            )
        ],
        source=source.source_ref(),
    )


def _load_static_source(source: DataSourceDefinition):
    try:
        static_path = _resolve_static_path(source)
    except ValueError as exc:
        return build_envelope(
            status="error",
            data=None,
            warnings=[ResolverWarning(code="source_invalid", message=str(exc))],
            source=source.source_ref(),
        )

    if not static_path.is_file():
        return build_envelope(
            status="error",
            data=None,
            warnings=[
                ResolverWarning(
                    code="source_unavailable",
                    message=f"Source file is missing: {source.path}",
                )
            ],
            source=source.source_ref(),
        )

    try:
        if source.format == "json":
            data = json.loads(static_path.read_text(encoding="utf-8"))
        else:
            data = yaml.safe_load(static_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError) as exc:
        return build_envelope(
            status="error",
            data=None,
            warnings=[
                ResolverWarning(
                    code="source_invalid",
                    message=f"Could not parse source {source.path}: {exc}",
                )
            ],
            source=source.source_ref(),
        )

    return build_envelope(
        status="ok",
        data=data,
        warnings=[],
        source=source.source_ref(),
    )


def _resolve_static_path(source: DataSourceDefinition) -> Path:
    if source.root_dir is None:
        raise ValueError("Static source root directory is not configured")
    if source.path is None:
        raise ValueError("Static source path is not configured")

    root_dir = source.root_dir.resolve()
    relative_path = Path(source.path)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError("Static source path must stay under the configured root")

    resolved_path = (root_dir / relative_path).resolve()
    if root_dir not in (resolved_path, *resolved_path.parents):
        raise ValueError("Static source path must stay under the configured root")

    return resolved_path
