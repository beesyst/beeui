from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from beeui_module.adapters.base import ProductUiAdapter
from beeui_module.adapters.beecap import BeeCapFixtureAdapter
from beeui_module.adapters.envelopes import AdapterErrorResult, AdapterResult

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "beecap"


# Хелпер: создание YAML fixture файлов в тестах
def _write_yaml(tmp_path: Path, filename: str, data: dict[str, Any]) -> Path:
    path = tmp_path / filename
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh)
    return path


# Тест: адаптер соответствует протоколу ProductUiAdapter (структурная типизация)
def test_beecap_adapter_implements_product_ui_adapter_protocol() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    as_protocol: ProductUiAdapter = adapter

    assert as_protocol.metadata.product_id == "beecap"
    assert as_protocol.metadata.title == "BeeCap"
    assert as_protocol.metadata.version == "0.1.0"
    assert as_protocol.metadata.capabilities == ("dashboard", "runs", "artifacts")
    assert as_protocol.metadata.supported_pages == ("/", "/runs")


# Тест: get_dashboard возвращает корректные данные из фикстуры, обрабатывает сценарии с отсутствующими данными и включает предупреждения
def test_dashboard_returns_ok_with_latest_run() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.get_dashboard()
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "ok"
    assert d["data"]["latest_run"]["id"] == "beecap_run_042"
    assert d["data"]["latest_run"]["status"] == "completed"
    # MRKT / Binance are present -> no warnings
    assert len(d["warnings"]) == 0
    assert d["meta"]["product"] == "beecap"
    assert d["meta"]["source"] == "fixture"


# Тест: MRKT и Binance summary fields присутствуют в дашборде, если они есть в данных фикстуры
def test_dashboard_includes_mrkt_summary_fields() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.get_dashboard().to_dict()
    mrkt = d["data"]["summary"]["mrkt"]
    assert mrkt["cycles_completed"] == 12
    assert mrkt["trades_executed"] == 48


# Тест: Binance summary fields присутствуют в дашборде, если они есть в данных фикстуры
def test_dashboard_includes_binance_summary_fields() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.get_dashboard().to_dict()
    binance = d["data"]["summary"]["binance"]
    assert binance["cycles_completed"] == 5
    assert binance["trades_executed"] == 22


# Тест: сценарий с отсутствующим latest_run возвращает статус partial с предупреждением
def test_no_latest_run_scenario(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path,
        "dashboard.yml",
        {
            "latest_run": None,
            "summary": {
                "mrkt": {"cycles_completed": 0, "trades_executed": 0},
                "binance": {"cycles_completed": 0, "trades_executed": 0},
            },
            "kpi_items": [{"label": "Total runs", "value": "0"}],
        },
    )
    _write_yaml(tmp_path, "runs.yml", {"runs": []})
    _write_yaml(tmp_path, "artifacts.yml", {"artifacts": {}})

    adapter = BeeCapFixtureAdapter(fixture_root=tmp_path)
    result = adapter.get_dashboard()
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "partial"
    assert d["data"]["latest_run"] is None
    codes = {w["code"] for w in d["warnings"]}
    assert "no_latest_run" in codes


# Тест: сценарий с отсутствующим Binance summary возвращает статус partial с предупреждением, MRKT при этом все еще присутствует
def test_partial_binance_scenario(tmp_path: Path) -> None:
    _write_yaml(
        tmp_path,
        "dashboard.yml",
        {
            "latest_run": {"id": "beecap_run_043", "status": "completed"},
            "summary": {
                "mrkt": {"cycles_completed": 8, "trades_executed": 32},
                "binance": None,
            },
            "kpi_items": [{"label": "Total runs", "value": "42"}],
        },
    )
    _write_yaml(tmp_path, "runs.yml", {"runs": []})
    _write_yaml(tmp_path, "artifacts.yml", {"artifacts": {}})

    adapter = BeeCapFixtureAdapter(fixture_root=tmp_path)
    result = adapter.get_dashboard()
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "partial"
    codes = {w["code"] for w in d["warnings"]}
    assert "binance_unavailable" in codes
    # MRKT is still present
    assert d["data"]["summary"]["mrkt"]["cycles_completed"] == 8


# Тест: при отсутствии fixture_root адаптер возвращает пустой дашборд со статусом ok
def test_no_fixture_root_returns_empty_dashboard() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=None)
    d = adapter.get_dashboard().to_dict()
    assert d["status"] == "ok"
    assert d["data"]["latest_run"] is None
    assert d["data"]["summary"] == {}


# Тест: при отсутствии summary fields в fixture данные дашборда возвращаются с предупреждениями, но не падают с ошибкой
def test_list_runs_returns_summaries() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.list_runs()
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "ok"
    assert len(d["data"]) == 3
    assert d["meta"]["count"] == 3
    assert d["data"][0]["id"] == "beecap_run_042"
    assert d["data"][1]["status"] == "failed"
    assert d["data"][2]["status"] == "running"


# Тест: get_run возвращает полные детали для валидного run ID, включая артефакты
def test_get_run_returns_detail() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.get_run("beecap_run_042")
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "ok"
    assert d["data"]["id"] == "beecap_run_042"
    assert d["data"]["status"] == "completed"
    assert d["data"]["started_at"] == "2026-06-01T10:00:00Z"
    assert d["data"]["completed_at"] == "2026-06-01T10:15:00Z"
    assert len(d["data"]["artifacts"]) == 4


# Тест: get_run для run в статусе "running" возвращает None для completed_at, не падая с ошибкой
def test_get_run_without_completed_at() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.get_run("beecap_run_040").to_dict()
    assert d["data"]["status"] == "running"
    assert d["data"]["completed_at"] is None


# Тест: get_run с невалидным ID возвращает ошибку с кодом invalid_id
def test_get_run_invalid_id_rejected() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.get_run("../beecap_run_042")
    assert isinstance(result, AdapterErrorResult)
    d = result.to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "invalid_id"


# Тест: get_run с несуществующим ID возвращает ошибку с кодом not_found
def test_get_run_not_found() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.get_run("nonexistent_run")
    assert isinstance(result, AdapterErrorResult)
    d = result.to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "not_found"


# Тест: list_artifacts возвращает артефактные ссылки для валидного run
def test_list_artifacts_returns_references() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.list_artifacts("beecap_run_042")
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "ok"
    artifact_ids = {a["artifact_id"] for a in d["data"]}
    assert "run_log" in artifact_ids
    assert "summary_report" in artifact_ids
    assert "trade_log" in artifact_ids
    assert d["meta"]["run_id"] == "beecap_run_042"


# Тест: list_artifacts для run без артефактов возвращает пустой список, не падая с ошибкой
def test_list_artifacts_empty_for_run_without_artifacts() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.list_artifacts("beecap_run_041").to_dict()
    assert d["status"] == "ok"
    assert d["data"] == []


# Тест: list_artifacts с невалидным run ID возвращает ошибку с кодом invalid_id
def test_list_artifacts_invalid_run_id_rejected() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.list_artifacts("../../etc/passwd").to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "invalid_id"


# Тест: list_artifacts с несуществующим run ID возвращает ошибку с кодом not_found
def test_list_artifacts_run_not_found() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.list_artifacts("nonexistent_run").to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "not_found"


# Тест: read_artifact возвращает содержимое артефакта для валидных run/artifact ID
def test_read_artifact_returns_content() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.read_artifact("beecap_run_042", "summary_report")
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "ok"
    assert d["data"]["artifact_id"] == "summary_report"
    assert d["data"]["content_type"] == "application/json"
    assert d["data"]["content"]["status"] == "completed"
    assert d["data"]["content"]["cycle_count"] == 12


# Тест: read_artifact для текстового артефакта возвращает plain text content
def test_read_artifact_text_content() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.read_artifact("beecap_run_042", "run_log").to_dict()
    assert d["status"] == "ok"
    assert "completed successfully" in d["data"]["content"]


# Тест: read_artifact для артефакта, помеченного как corrupted, возвращает статус partial с предупреждением
def test_read_artifact_invalid_artifact_id_rejected() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.read_artifact("beecap_run_042", "../run_log").to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "invalid_id"


# Тест: read_artifact для несуществующего артефакта возвращает ошибку с кодом not_found
def test_read_artifact_invalid_run_id_rejected() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.read_artifact("../../run", "run_log").to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "invalid_id"


# Тест: read_artifact для несуществующего артефакта возвращает ошибку с кодом not_found
def test_read_artifact_not_found() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.read_artifact("beecap_run_042", "nonexistent_artifact").to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "not_found"


# Тест: read_artifact для несуществующего run ID возвращает ошибку с кодом not_found
def test_read_artifact_run_not_found() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.read_artifact("beecap_run_999", "run_log").to_dict()
    assert d["status"] == "error"
    assert d["error"]["code"] == "not_found"


# Тест: read_artifact для артефакта, помеченного как corrupted, возвращает статус partial с предупреждением
def test_corrupted_artifact_returns_partial() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    result = adapter.read_artifact("beecap_run_042", "corrupted_file")
    assert isinstance(result, AdapterResult)
    d = result.to_dict()

    assert d["status"] == "partial"
    assert d["data"]["content"] is None
    codes = {w["code"] for w in d["warnings"]}
    assert "artifact_corrupted" in codes


# Тест: get_dashboard возвращает статус partial с предупреждениями при отсутствии latest_run и summary fields, но не падает с ошибкой
def test_config_read_model_returns_fixture_mode() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    d = adapter.get_config_read_model().to_dict()
    assert d["status"] == "ok"
    assert d["data"]["product"] == "beecap"
    assert d["data"]["mode"] == "fixture"
    assert d["data"]["read_only"] is True
    assert d["data"]["editable"] is False


# Тест: адаптерные методы не возвращают секреты и чувствительные данные в рамках своих envelope-ответов
def test_no_secrets_in_envelopes() -> None:
    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    dashboard = str(adapter.get_dashboard().to_dict())
    runs = str(adapter.list_runs().to_dict())
    artifact = str(adapter.read_artifact("beecap_run_042", "summary_report").to_dict())

    secret_patterns = ("secret", "token", "password", "api_key", "api_secret")
    for field in (dashboard, runs, artifact):
        for pattern in secret_patterns:
            assert pattern not in field.lower()


# Тест: методы адаптера, которые должны быть read-only, не мутируют исходные fixture файлы
def test_source_fixtures_not_mutated() -> None:
    original_dashboard = (FIXTURE_ROOT / "dashboard.yml").read_bytes()

    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)
    adapter.get_dashboard()
    adapter.list_runs()
    adapter.get_run("beecap_run_042")
    adapter.list_artifacts("beecap_run_042")
    adapter.read_artifact("beecap_run_042", "summary_report")

    after = (FIXTURE_ROOT / "dashboard.yml").read_bytes()
    assert after == original_dashboard


# Тест: методы адаптера, которые не реализованы и должны быть недоступны, возвращают ошибку с кодом unavailable
def test_optional_methods_raise_unavailable() -> None:
    from beeui_module.adapters.envelopes import error_result_from_exception
    from beeui_module.adapters.errors import UnavailableError

    adapter = BeeCapFixtureAdapter(fixture_root=FIXTURE_ROOT)

    for method_name, args in [
        ("validate_config_candidate", ({"key": "val"},)),
        ("list_actions", ()),
        ("preview_action", ("action_001", {"key": "val"})),
        ("execute_action", ("action_001", {"key": "val"})),
    ]:
        try:
            getattr(adapter, method_name)(*args)
            raise AssertionError(f"{method_name} must raise UnavailableError")
        except UnavailableError as exc:
            d = error_result_from_exception(exc).to_dict()
            assert d["status"] == "error"
            assert d["error"]["code"] == "unavailable"
            assert method_name in d["error"]["message"]
