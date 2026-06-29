from __future__ import annotations

from beeui_module.data.models import (
    DataSourceDefinition,
    ResolverEnvelope,
    ResolverWarning,
    build_envelope,
)
from beeui_module.data.selectors import select_data, validate_selector
from beeui_module.data.sources import load_source_data


class DataResolver:
    def __init__(self, data_sources: dict[str, DataSourceDefinition]) -> None:
        self._data_sources = data_sources
        self._cache: dict[str, ResolverEnvelope] = {}

    def resolve(self, source_id: str, selector: str | None = None) -> ResolverEnvelope:
        source = self._data_sources.get(source_id)
        if source is None:
            return build_envelope(
                status="error",
                data=None,
                warnings=[
                    ResolverWarning(
                        code="source_missing",
                        message=f"Unknown data source: {source_id}",
                    )
                ],
                source={"type": "unknown", "id": source_id},
            )

        source_envelope = self._load_source(source)
        if selector is None or source_envelope.status == "error":
            return source_envelope

        try:
            validate_selector(selector)
        except ValueError as exc:
            return build_envelope(
                status="error",
                data=None,
                warnings=[ResolverWarning(code="selector_invalid", message=str(exc))],
                source=source.source_ref(),
            )

        try:
            selected = select_data(source_envelope.data, selector)
        except KeyError:
            return build_envelope(
                status="partial",
                data=None,
                warnings=[
                    ResolverWarning(
                        code="selector_missing",
                        message=f"Selector not found: {selector}",
                    )
                ],
                source=source.source_ref(),
            )

        return build_envelope(
            status="ok",
            data=selected,
            warnings=list(source_envelope.warnings),
            source=source.source_ref(),
        )

    def _load_source(self, source: DataSourceDefinition) -> ResolverEnvelope:
        cached = self._cache.get(source.source_id)
        if cached is None:
            cached = load_source_data(source)
            self._cache[source.source_id] = cached
        return cached
