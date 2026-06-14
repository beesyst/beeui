from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Protocol

from beeui_module.adapters.envelopes import (
    AdapterErrorResult,
    AdapterMetadata,
    AdapterResult,
    error_result_from_exception,
)
from beeui_module.adapters.errors import UnavailableError


# Интерфейс адаптера для продуктов и базовая реализация
class ProductUiAdapter(Protocol):
    metadata: AdapterMetadata

    def get_dashboard(self) -> AdapterResult | AdapterErrorResult: ...

    def list_runs(self) -> AdapterResult | AdapterErrorResult: ...

    def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult: ...

    def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult: ...

    def read_artifact(
        self, run_id: str, artifact_id: str
    ) -> AdapterResult | AdapterErrorResult: ...

    def get_config_read_model(self) -> AdapterResult | AdapterErrorResult: ...

    def validate_config_candidate(
        self, candidate: dict[str, Any]
    ) -> AdapterResult | AdapterErrorResult: ...

    def apply_config_candidate(
        self,
        candidate: dict[str, Any],
        expected_hash: str | None = None,
        actor: dict[str, str] | None = None,
    ) -> AdapterResult | AdapterErrorResult: ...

    def list_actions(self) -> AdapterResult | AdapterErrorResult: ...

    def preview_action(
        self, action_id: str, payload: dict[str, Any]
    ) -> AdapterResult | AdapterErrorResult: ...

    def execute_action(
        self,
        action_id: str,
        payload: dict[str, Any],
        actor: dict[str, str] | None = None,
    ) -> AdapterResult | AdapterErrorResult: ...


# Базовая реализация адаптера с не реализованными методами
class ProductUiAdapterBase(ABC):
    def __init__(self, metadata: AdapterMetadata) -> None:
        self.metadata = metadata

    @abstractmethod
    def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
        raise NotImplementedError

    @abstractmethod
    def list_runs(self) -> AdapterResult | AdapterErrorResult:
        raise NotImplementedError

    @abstractmethod
    def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
        raise NotImplementedError

    def get_venue_dashboard(self, venue_id: str) -> AdapterResult | AdapterErrorResult:
        return error_result_from_exception(
            UnavailableError("Venue dashboard is unavailable")
        )

    def get_page(
        self, page_id: str, query: Mapping[str, str]
    ) -> AdapterResult | AdapterErrorResult:
        return error_result_from_exception(
            UnavailableError(f"Page {page_id} is unavailable")
        )

    @abstractmethod
    def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
        raise NotImplementedError

    @abstractmethod
    def read_artifact(
        self, run_id: str, artifact_id: str
    ) -> AdapterResult | AdapterErrorResult:
        raise NotImplementedError

    @abstractmethod
    def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
        raise NotImplementedError

    def validate_config_candidate(
        self, candidate: dict[str, Any]
    ) -> AdapterResult | AdapterErrorResult:
        raise UnavailableError(
            "Optional method validate_config_candidate is unavailable"
        )

    def apply_config_candidate(
        self,
        candidate: dict[str, Any],
        expected_hash: str | None = None,
        actor: dict[str, str] | None = None,
    ) -> AdapterResult | AdapterErrorResult:
        raise UnavailableError("Optional method apply_config_candidate is unavailable")

    def list_actions(self) -> AdapterResult | AdapterErrorResult:
        raise UnavailableError("Optional method list_actions is unavailable")

    def preview_action(
        self, action_id: str, payload: dict[str, Any]
    ) -> AdapterResult | AdapterErrorResult:
        raise UnavailableError("Optional method preview_action is unavailable")

    def execute_action(
        self,
        action_id: str,
        payload: dict[str, Any],
        actor: dict[str, str] | None = None,
    ) -> AdapterResult | AdapterErrorResult:
        raise UnavailableError("Optional method execute_action is unavailable")
