from __future__ import annotations

from pathlib import Path

from beeui_module.data.models import DataSourceDefinition
from beeui_module.data.resolver import DataResolver
from beeui_module.data.selectors import select_data, validate_selector
from beeui_module.data.sources import load_source_data
from beeui_module.pages.config import load_beeui_config


# Тест: загрузка данных из demo источника и базовая работа резолвера с селекторами
def test_demo_source_loads() -> None:
    source = DataSourceDefinition(source_id="demo_dashboard", source_type="demo")

    envelope = load_source_data(source).to_dict()

    assert envelope["status"] == "ok"
    assert envelope["source"] == {"type": "demo", "id": "demo_dashboard"}
    assert envelope["warnings"] == []
    assert envelope["data"]["dashboard"]["latest_run"]["id"] == "run_demo_001"


# Тест: загрузка данных из static источника в формате yaml и json, с поддержкой вложенных селекторов и списков
def test_static_yaml_source_loads() -> None:
    source = DataSourceDefinition(
        source_id="static_dashboard",
        source_type="static",
        format="yaml",
        path="tests/fixtures/demo_static/dashboard.yml",
        root_dir=Path.cwd(),
    )

    envelope = load_source_data(source).to_dict()

    assert envelope["status"] == "ok"
    assert envelope["data"]["dashboard"]["latest_run"]["id"] == "run_yaml_001"


# Тест: загрузка данных из static источника в формате json, с поддержкой вложенных селекторов и списков
def test_static_json_source_loads() -> None:
    source = DataSourceDefinition(
        source_id="static_dashboard",
        source_type="static",
        format="json",
        path="tests/fixtures/demo_static/dashboard.json",
        root_dir=Path.cwd(),
    )

    envelope = load_source_data(source).to_dict()

    assert envelope["status"] == "ok"
    assert envelope["data"]["runs"][0]["id"] == "run_json_001"


# Тест: invalid selector syntax в резолвере должен возвращать envelope с ошибкой и предупреждением
def test_selector_scalar_nested_and_list_success() -> None:
    payload = {
        "dashboard": {
            "latest_run": {"id": "run_demo_001", "status": "ok"},
            "kpis": {"total_runs": 24},
        },
        "runs": [{"id": "run_demo_001"}],
    }

    assert select_data(payload, "dashboard.latest_run.id") == "run_demo_001"
    assert select_data(payload, "dashboard.kpis.total_runs") == 24
    assert select_data(payload, "runs[0].id") == "run_demo_001"


# Тест: missing selector должен возвращать envelope со статусом partial и предупреждением
def test_selector_missing_returns_partial_envelope() -> None:
    resolver = DataResolver(
        {
            "demo_dashboard": DataSourceDefinition(
                source_id="demo_dashboard", source_type="demo"
            )
        }
    )

    envelope = resolver.resolve(
        "demo_dashboard", "dashboard.latest_run.missing"
    ).to_dict()

    assert envelope == {
        "status": "partial",
        "data": None,
        "warnings": [
            {
                "code": "selector_missing",
                "message": "Selector not found: dashboard.latest_run.missing",
            }
        ],
        "source": {"type": "demo", "id": "demo_dashboard"},
    }


# Тест: invalid selector syntax должен возвращать envelope со статусом error и предупреждением
def test_invalid_selector_returns_error_envelope() -> None:
    resolver = DataResolver(
        {
            "demo_dashboard": DataSourceDefinition(
                source_id="demo_dashboard", source_type="demo"
            )
        }
    )

    envelope = resolver.resolve("demo_dashboard", "dashboard..latest_run").to_dict()

    assert envelope["status"] == "error"
    assert envelope["warnings"] == [
        {
            "code": "selector_invalid",
            "message": "Invalid selector syntax: dashboard..latest_run",
        }
    ]


# Тест: invalid source id должен возвращать envelope со статусом error и предупреждением
def test_invalid_source_is_handled_explicitly() -> None:
    resolver = DataResolver({})

    envelope = resolver.resolve("missing_source", "dashboard.latest_run.id").to_dict()

    assert envelope["status"] == "error"
    assert envelope["source"] == {"type": "unknown", "id": "missing_source"}
    assert envelope["warnings"] == [
        {
            "code": "source_missing",
            "message": "Unknown data source: missing_source",
        }
    ]


# Тест: форма envelope стабильна и всегда содержит определённые ключи, даже при ошибках разрешения данных
def test_envelope_shape_is_stable() -> None:
    resolver = DataResolver(
        {
            "demo_dashboard": DataSourceDefinition(
                source_id="demo_dashboard", source_type="demo"
            )
        }
    )

    envelope = resolver.resolve("demo_dashboard", "dashboard.latest_run.id").to_dict()

    assert set(envelope) == {"status", "data", "warnings", "source"}
    assert envelope["status"] == "ok"
    assert envelope["source"] == {"type": "demo", "id": "demo_dashboard"}


# Тест: invalid selector syntax в резолвере должен возвращать envelope с ошибкой и предупреждением
def test_no_eval_or_method_call_selector_syntax_accepted() -> None:
    invalid_selectors = [
        "dashboard.latest_run.get('id')",
        "dashboard.__class__",
        "dashboard['latest_run']",
        "dashboard.latest_run()",
    ]

    for selector in invalid_selectors:
        try:
            validate_selector(selector)
        except ValueError as exc:
            assert str(exc) == f"Invalid selector syntax: {selector}"
        else:
            raise AssertionError(f"selector must be rejected: {selector}")


# Тест: загрузка данных из demo источника через конфиг и базовая работа резолвера с селекторами
def test_schema_level_static_source_loads() -> None:
    config = load_beeui_config(Path("config/schema.yml"))

    assert config.data_sources["demo_dashboard"].source_type == "demo"
