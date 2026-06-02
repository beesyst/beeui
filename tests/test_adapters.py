from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from beeui_module.adapters.base import ProductUiAdapter, ProductUiAdapterBase
from beeui_module.adapters.envelopes import (
    AdapterMetadata,
    error_result_from_exception,
    ok_result,
)
from beeui_module.adapters.errors import (
    InvalidIdError,
    NotFoundError,
    UnavailableError,
)
from beeui_module.adapters.ids import (
    validate_action_id,
    validate_artifact_id,
    validate_product_id,
    validate_run_id,
)


# Фейковый адаптер для тестирования контрактов и базовой логики
class FakeAdapter(ProductUiAdapterBase):
    def __init__(self) -> None:
        super().__init__(
            AdapterMetadata(
                product_id="demo",
                title="Demo Product",
                version="0.1.0",
                capabilities=("dashboard", "runs", "artifacts", "config_read"),
                supported_pages=("/", "/runs"),
            )
        )
        self._dashboard = {
            "latest_run": {"id": "run_001", "status": "ok"},
            "summary": {"text": "Demo dashboard payload"},
        }
        self._runs = [
            {
                "id": "run_001",
                "status": "ok",
                "artifacts": {
                    "report_json": {
                        "content_type": "application/json",
                        "content": {"score": 0.9},
                    },
                    "log_txt": {
                        "content_type": "text/plain",
                        "content": "run ok",
                    },
                },
            },
            {
                "id": "run_002",
                "status": "partial",
                "artifacts": {},
            },
        ]

    def get_dashboard(self):
        return ok_result(deepcopy(self._dashboard), meta={"adapter": "fake"})

    def list_runs(self):
        runs = [{"id": run["id"], "status": run["status"]} for run in self._runs]
        return ok_result(deepcopy(runs), meta={"count": len(runs)})

    def get_run(self, run_id: str):
        try:
            safe_run_id = validate_run_id(run_id)
            for run in self._runs:
                if run["id"] == safe_run_id:
                    return ok_result(
                        deepcopy({"id": run["id"], "status": run["status"]})
                    )
            raise NotFoundError(f"Run not found: {safe_run_id}")
        except Exception as exc:
            return error_result_from_exception(exc)

    def list_artifacts(self, run_id: str):
        try:
            safe_run_id = validate_run_id(run_id)
            for run in self._runs:
                if run["id"] != safe_run_id:
                    continue
                artifacts = [
                    {
                        "artifact_id": artifact_id,
                        "content_type": artifact["content_type"],
                    }
                    for artifact_id, artifact in run["artifacts"].items()
                ]
                return ok_result(artifacts)
            raise NotFoundError(f"Run not found: {safe_run_id}")
        except Exception as exc:
            return error_result_from_exception(exc)

    def read_artifact(self, run_id: str, artifact_id: str):
        try:
            safe_run_id = validate_run_id(run_id)
            safe_artifact_id = validate_artifact_id(artifact_id)
            for run in self._runs:
                if run["id"] != safe_run_id:
                    continue
                artifact = run["artifacts"].get(safe_artifact_id)
                if artifact is None:
                    raise NotFoundError(
                        f"Artifact not found: {safe_artifact_id} for run {safe_run_id}"
                    )
                payload = {
                    "artifact_id": safe_artifact_id,
                    "content_type": artifact["content_type"],
                    "content": deepcopy(artifact["content"]),
                }
                return ok_result(payload)
            raise NotFoundError(f"Run not found: {safe_run_id}")
        except Exception as exc:
            return error_result_from_exception(exc)

    def get_config_read_model(self):
        return ok_result(
            {
                "mode": "demo",
                "read_only": True,
                "editable": False,
            }
        )


# Тест: чек, что фейковый адаптер соответствует контракту и базовая логика работает как ожидается
def test_product_ui_adapter_contract_is_importable() -> None:
    adapter = FakeAdapter()
    as_protocol: ProductUiAdapter = adapter

    assert as_protocol.metadata.product_id == "demo"
    assert as_protocol.metadata.title == "Demo Product"
    assert as_protocol.metadata.version == "0.1.0"
    assert as_protocol.metadata.capabilities == (
        "dashboard",
        "runs",
        "artifacts",
        "config_read",
    )
    assert as_protocol.metadata.supported_pages == ("/", "/runs")


# Тест: чек, что методы адаптера возвращают данные в правильной форме и обрабатывают ошибки корректно
def test_fake_adapter_dashboard_runs_run_detail_and_config() -> None:
    adapter = FakeAdapter()

    dashboard = adapter.get_dashboard().to_dict()
    runs = adapter.list_runs().to_dict()
    run_detail = adapter.get_run("run_001").to_dict()
    config_model = adapter.get_config_read_model().to_dict()

    assert dashboard["status"] == "ok"
    assert dashboard["data"]["latest_run"]["id"] == "run_001"
    assert runs["status"] == "ok"
    assert runs["data"][0]["id"] == "run_001"
    assert run_detail == {
        "status": "ok",
        "data": {"id": "run_001", "status": "ok"},
        "warnings": [],
        "meta": {},
    }
    assert config_model["status"] == "ok"
    assert config_model["data"]["read_only"] is True


# Тест: чек, что адаптер корректно обрабатывает невалидные идентификаторы и возвращает ошибки в правильной форме
def test_fake_adapter_lists_and_reads_artifacts() -> None:
    adapter = FakeAdapter()

    artifacts = adapter.list_artifacts("run_001").to_dict()
    artifact = adapter.read_artifact("run_001", "report_json").to_dict()

    assert artifacts["status"] == "ok"
    assert artifacts["data"] == [
        {"artifact_id": "report_json", "content_type": "application/json"},
        {"artifact_id": "log_txt", "content_type": "text/plain"},
    ]
    assert artifact["status"] == "ok"
    assert artifact["data"]["artifact_id"] == "report_json"
    assert artifact["data"]["content"]["score"] == 0.9


# Тест: чек, что невалидные идентификаторы для запусков и артефактов корректно отклоняются с ошибкой invalid_id
def test_invalid_run_id_and_artifact_id_are_rejected() -> None:
    adapter = FakeAdapter()

    invalid_run = adapter.get_run("../run_001").to_dict()
    invalid_artifact = adapter.read_artifact("run_001", "../report_json").to_dict()

    assert invalid_run["status"] == "error"
    assert invalid_run["error"]["code"] == "invalid_id"
    assert invalid_artifact["status"] == "error"
    assert invalid_artifact["error"]["code"] == "invalid_id"


# Тест: чек, что запрос несуществующего запуска возвращает ошибку not_found в правильной форме
def test_not_found_error_envelope_shape_is_stable() -> None:
    adapter = FakeAdapter()

    missing_run = adapter.get_run("run_999").to_dict()

    assert missing_run == {
        "status": "error",
        "error": {"code": "not_found", "message": "Run not found: run_999"},
        "warnings": [],
        "meta": {},
    }


def test_generic_exception_error_envelope_does_not_leak_raw_message() -> None:
    envelope = error_result_from_exception(RuntimeError("secret token abc123")).to_dict()

    assert envelope["status"] == "error"
    assert envelope["error"] == {"code": "adapter_error", "message": "Adapter error"}
    assert "secret" not in str(envelope)
    assert "abc123" not in str(envelope)


def test_adapter_metadata_rejects_empty_or_non_string_fields() -> None:
    invalid_metadata_args = [
        {"title": "", "version": "0.1.0"},
        {"title": "   ", "version": "0.1.0"},
        {"title": 123, "version": "0.1.0"},
        {"title": "Demo Product", "version": ""},
        {"title": "Demo Product", "version": "   "},
        {"title": "Demo Product", "version": 123},
        {
            "title": "Demo Product",
            "version": "0.1.0",
            "capabilities": ("dashboard", ""),
        },
        {
            "title": "Demo Product",
            "version": "0.1.0",
            "capabilities": ("dashboard", 123),
        },
        {
            "title": "Demo Product",
            "version": "0.1.0",
            "supported_pages": ("/", ""),
        },
        {
            "title": "Demo Product",
            "version": "0.1.0",
            "supported_pages": ("/", 123),
        },
    ]

    for kwargs in invalid_metadata_args:
        try:
            AdapterMetadata(product_id="demo", **kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"Metadata args must be rejected: {kwargs}")


AdapterMethodCall = tuple[str, Callable[..., Any], tuple[Any, ...]]


# Тест: чек, что необязательные методы по умолчанию недоступны и возвращают ошибку unavailable при вызове
def test_optional_methods_are_unavailable_by_default() -> None:
    adapter = FakeAdapter()

    unavailable_contracts: list[AdapterMethodCall] = [
        (
            "validate_config_candidate",
            adapter.validate_config_candidate,
            ({"candidate": "value"},),
        ),
        ("list_actions", adapter.list_actions, ()),
        ("preview_action", adapter.preview_action, ("action_demo", {"x": 1})),
        ("execute_action", adapter.execute_action, ("action_demo", {"x": 1})),
    ]

    for method_name, method, args in unavailable_contracts:
        try:
            method(*args)
        except UnavailableError as exc:
            envelope = error_result_from_exception(exc).to_dict()
            assert envelope["status"] == "error"
            assert envelope["error"]["code"] == "unavailable"
            assert method_name in envelope["error"]["message"]
        else:
            raise AssertionError(f"{method_name} must raise UnavailableError")


# Тест: чек, что методы, которые не должны мутировать состояние адаптера, действительно его не мутируют
def test_read_only_methods_do_not_mutate_fake_adapter_state() -> None:
    adapter = FakeAdapter()

    first_runs = adapter.list_runs().to_dict()
    first_runs["data"][0]["id"] = "mutated"

    second_runs = adapter.list_runs().to_dict()

    assert second_runs["data"][0]["id"] == "run_001"


# Тест: чек, что хелперы для валидации идентификаторов отклоняют небезопасные значения и возвращают ошибки с кодом invalid_id
def test_safe_id_helpers_reject_unsafe_values() -> None:
    invalid_values = [
        "",
        "   ",
        "..",
        "../run_1",
        "run/1",
        "run\\1",
        "/abs",
        "https://example",
        "run?id=1",
        "run;rm",
        "~run",
        "-run",
    ]

    validators = [
        validate_product_id,
        validate_run_id,
        validate_artifact_id,
        validate_action_id,
    ]

    for value in invalid_values:
        for validator in validators:
            try:
                validator(value)
            except InvalidIdError:
                pass
            else:
                raise AssertionError(f"Value must be rejected: {value}")
