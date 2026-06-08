from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from beeui_module.adapters.base import ProductUiAdapterBase
from beeui_module.adapters.envelopes import (
    AdapterMetadata,
    AdapterWarning,
    error_result,
    ok_result,
    partial_result,
)
from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.web.app import create_beeui_app, mount_beeui


# Класс: полный тестовый адаптер для HTML/API сценариев продуктовой консоли
class FakeProductConsoleAdapter(ProductUiAdapterBase):
    def __init__(self) -> None:
        super().__init__(
            AdapterMetadata(
                product_id="fake_product",
                title="Fake Product",
                version="1.2.3",
                capabilities=("dashboard", "runs", "artifacts", "venues"),
                supported_pages=("/", "/runs", "/venues/{venue_id}"),
            )
        )

    def get_dashboard(self) -> Any:
        return partial_result(
            {
                "latest_run": {
                    "id": "run_safe_001",
                    "status": '<script>alert("x")</script>',
                },
                "summary": {
                    "mode": "paper",
                    "health": "degraded",
                },
                "kpi_items": [
                    {"label": "Total runs", "value": "12"},
                    {"label": "Healthy venues", "value": "2"},
                ],
                "raw_html": '<img src=x onerror="alert(1)">',
            },
            warnings=[
                AdapterWarning(
                    code="partial_data",
                    message="Dashboard is degraded",
                )
            ],
            meta={"source": "fake", "product": "fake_product"},
        )

    def list_runs(self) -> Any:
        return ok_result(
            [
                {
                    "id": "run_safe_001",
                    "status": "completed",
                    "started_at": "2026-06-06T10:00:00Z",
                    "completed_at": "2026-06-06T10:05:00Z",
                },
                {
                    "id": "run_safe_002",
                    "status": "running",
                    "started_at": "2026-06-06T10:07:00Z",
                },
            ],
            meta={"count": 2},
        )

    def get_run(self, run_id: str) -> Any:
        if run_id == "run_error_001":
            return error_result("not_found", "Run not found")
        return ok_result(
            {
                "id": run_id,
                "status": "completed",
                "started_at": "2026-06-06T10:00:00Z",
                "completed_at": "2026-06-06T10:05:00Z",
                "artifacts": [
                    {
                        "artifact_id": "report_json",
                        "content_type": "application/json",
                    }
                ],
            },
            meta={"run_id": run_id},
        )

    def get_venue_dashboard(self, venue_id: str) -> Any:
        if venue_id == "venue_partial_001":
            return partial_result(
                {
                    "venue_id": venue_id,
                    "status": "degraded",
                    "balance": "n/a",
                },
                warnings=[
                    AdapterWarning(
                        code="venue_partial",
                        message="Venue data is partial",
                    )
                ],
                meta={"venue_id": venue_id},
            )
        return ok_result(
            {
                "venue_id": venue_id,
                "status": "healthy",
                "balance": "1200.50",
            },
            meta={"venue_id": venue_id},
        )

    def list_artifacts(self, run_id: str) -> Any:
        return ok_result([])

    def read_artifact(self, run_id: str, artifact_id: str) -> Any:
        return ok_result(
            {
                "artifact_id": artifact_id,
                "content_type": "application/json",
                "content": {"ok": True},
            }
        )

    def get_config_read_model(self) -> Any:
        return ok_result({"read_only": True})


# Класс: legacy-адаптер намеренно не реализует новые необязательные методы протокола
class LegacyProductConsoleAdapter:
    def __init__(self) -> None:
        self.metadata = AdapterMetadata(
            product_id="legacy_product",
            title="Legacy Product",
            version="1.0.0",
        )

    def get_dashboard(self) -> Any:
        return ok_result({})

    def list_runs(self) -> Any:
        return ok_result([])

    def get_run(self, run_id: str) -> Any:
        return ok_result({"id": run_id})

    def list_artifacts(self, run_id: str) -> Any:
        return ok_result([])

    def read_artifact(self, run_id: str, artifact_id: str) -> Any:
        return ok_result({})

    def get_config_read_model(self) -> Any:
        return ok_result({"read_only": True})


# Тест: dashboard корректно отображается в HTML и возвращается через API
def test_adapter_dashboard_html_and_api_work() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    html = client.get("/")
    api = client.get("/api/dashboard")

    assert html.status_code == 200
    assert "Dashboard" in html.text
    assert "run_safe_001" in html.text
    assert "&lt;script&gt;alert" in html.text or "\\u003cscript\\u003e" in html.text
    assert "<script>alert" not in html.text

    assert api.status_code == 200
    payload = api.json()
    assert payload["ok"] is True
    assert payload["api"] == "beeui.v0"
    assert payload["read_only"] is True
    assert payload["data"]["latest_run"]["id"] == "run_safe_001"
    assert payload["meta"]["status"] == "partial"


# Тест: список запусков доступен в HTML и API с метаданными адаптера
def test_adapter_runs_html_and_api_work() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    html = client.get("/runs")
    api = client.get("/api/runs")

    assert html.status_code == 200
    assert "Run list" in html.text
    assert "run_safe_002" in html.text

    assert api.status_code == 200
    payload = api.json()
    assert payload["ok"] is True
    assert len(payload["data"]) == 2
    assert payload["meta"]["count"] == 2


# Тест: детали запуска и связанные артефакты доступны в HTML и API
def test_adapter_run_detail_html_and_api_work() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    html = client.get("/runs/run_safe_001")
    api = client.get("/api/runs/run_safe_001")

    assert html.status_code == 200
    assert "Run run_safe_001" in html.text
    assert "report_json" in html.text

    assert api.status_code == 200
    payload = api.json()
    assert payload["ok"] is True
    assert payload["data"]["id"] == "run_safe_001"


# Тест: venue dashboard отображается в HTML и возвращается через API
def test_adapter_venue_dashboard_html_and_api_work() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    html = client.get("/venues/venue_safe_001")
    api = client.get("/api/venues/venue_safe_001/dashboard")

    assert html.status_code == 200
    assert "Venue venue_safe_001" in html.text
    assert "healthy" in html.text

    assert api.status_code == 200
    payload = api.json()
    assert payload["ok"] is True
    assert payload["data"]["venue_id"] == "venue_safe_001"


# Тест: отсутствующий optional venue method даёт явный unavailable envelope
def test_legacy_adapter_without_venue_method_is_supported() -> None:
    legacy_adapter = LegacyProductConsoleAdapter()
    app = create_beeui_app(adapter=cast(Any, legacy_adapter))
    client = TestClient(app)

    response = client.get("/api/venues/venue_safe_001/dashboard")

    assert response.status_code == 503
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == {
        "code": "unavailable",
        "message": "Adapter method get_venue_dashboard is unavailable",
    }


# Тест: небезопасные идентификаторы отклоняются до вызова адаптера
def test_invalid_ids_are_rejected() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    invalid_run_html = client.get("/runs/../bad")
    invalid_run_api = client.get("/api/runs/bad;id")
    invalid_venue_html = client.get("/venues/bad;venue")
    invalid_venue_api = client.get("/api/venues/bad;venue/dashboard")

    assert invalid_run_html.status_code in {400, 404}
    assert invalid_run_api.status_code == 400
    assert invalid_run_api.json()["error"]["code"] == "invalid_id"
    assert invalid_venue_html.status_code == 400
    assert invalid_venue_api.status_code == 400
    assert invalid_venue_api.json()["error"]["code"] == "invalid_id"


# Тест: ошибочные и частичные состояния адаптера сохраняются в API envelope
def test_not_found_and_partial_states_are_explicit() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    missing_run = client.get("/api/runs/run_error_001")
    partial_venue = client.get("/api/venues/venue_partial_001/dashboard")

    assert missing_run.status_code == 404
    assert missing_run.json()["ok"] is False
    assert missing_run.json()["error"]["code"] == "not_found"

    assert partial_venue.status_code == 200
    assert partial_venue.json()["ok"] is True
    assert partial_venue.json()["meta"]["status"] == "partial"


# Тест: без адаптера приложение продолжает работать в demo mode
def test_demo_mode_still_uses_configured_pages_without_adapter() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Demo operator dashboard" in response.text
    assert client.get("/api/dashboard").status_code == 404


# Тест: HTML-ссылки учитывают route prefix и FastAPI mount path
def test_route_prefix_and_embedded_mount_work_for_product_console() -> None:
    settings = load_settings(settings_path())
    settings["web"]["route_prefix"] = "/bee"

    prefixed_app = create_beeui_app(
        settings=settings,
        adapter=FakeProductConsoleAdapter(),
    )
    prefixed_client = TestClient(prefixed_app)

    prefixed_dashboard = prefixed_client.get("/bee/")
    assert prefixed_dashboard.status_code == 200
    assert 'href="/bee/runs/run_safe_001"' in prefixed_dashboard.text
    assert prefixed_client.get("/bee/api/dashboard").status_code == 200
    assert prefixed_client.get("/").status_code == 404

    parent = FastAPI()
    mount_beeui(parent, path="/ui", adapter=FakeProductConsoleAdapter())
    mounted_client = TestClient(parent)

    mounted_dashboard = mounted_client.get("/ui/")
    assert mounted_dashboard.status_code == 200
    assert 'href="/ui/runs/run_safe_001"' in mounted_dashboard.text
    assert mounted_client.get("/ui/api/runs").status_code == 200
    assert mounted_client.get("/ui/venues/venue_safe_001").status_code == 200
    mounted_run = mounted_client.get("/ui/runs/run_safe_001")
    assert mounted_run.status_code == 200
    assert 'href="/ui/runs/run_safe_001/artifacts/report_json"' in mounted_run.text


# Тест: экранирование значения адаптера перед выводом в HTML
def test_html_escapes_adapter_values() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert '<img src=x onerror="alert(1)">' not in response.text
    assert "\\u003cimg" in response.text or "&lt;img" in response.text


# Тест: API отклоняет dashboard payload неверного типа
def test_malformed_dashboard_api_is_rejected() -> None:
    class MalformedDashboardAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(["not", "an", "object"])

    client = TestClient(create_beeui_app(adapter=MalformedDashboardAdapter()))

    response = client.get("/api/dashboard")

    assert response.status_code == 502
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "malformed_adapter_payload"
    assert (
        payload["error"]["message"] == "Adapter returned non-object dashboard payload"
    )


# Тест: API отклоняет runs payload неверного типа
def test_malformed_runs_api_is_rejected() -> None:
    class MalformedRunsAdapter(FakeProductConsoleAdapter):
        def list_runs(self) -> Any:
            return ok_result({"not": "a list"})

    client = TestClient(create_beeui_app(adapter=MalformedRunsAdapter()))

    response = client.get("/api/runs")

    assert response.status_code == 502
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "malformed_adapter_payload"


# Тест: API отклоняет run detail payload неверного типа
def test_malformed_run_detail_api_is_rejected() -> None:
    class MalformedRunAdapter(FakeProductConsoleAdapter):
        def get_run(self, run_id: str) -> Any:
            return ok_result(["not", "an", "object"])

    client = TestClient(create_beeui_app(adapter=MalformedRunAdapter()))

    response = client.get("/api/runs/run_safe_001")

    assert response.status_code == 502
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "malformed_adapter_payload"


# Тест: API отклоняет venue payload неверного типа
def test_malformed_venue_api_is_rejected() -> None:
    class MalformedVenueAdapter(FakeProductConsoleAdapter):
        def get_venue_dashboard(self, venue_id: str) -> Any:
            return ok_result(["not", "an", "object"])

    client = TestClient(create_beeui_app(adapter=MalformedVenueAdapter()))

    response = client.get("/api/venues/venue_safe_001/dashboard")

    assert response.status_code == 502
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"]["code"] == "malformed_adapter_payload"


# Тест: секреты в dashboard payload редактируются для HTML и API
def test_dashboard_secrets_are_redacted_in_html_and_api() -> None:
    class SecretDashboardAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "summary": {
                        "api_key": "sk-live-probe",
                        "nested": {"token": "token-live-probe"},
                    },
                    "plain": "safe-value",
                }
            )

    client = TestClient(create_beeui_app(adapter=SecretDashboardAdapter()))

    html = client.get("/")
    api = client.get("/api/dashboard")

    assert "sk-live-probe" not in html.text
    assert "token-live-probe" not in html.text
    assert "sk-live-probe" not in api.text
    assert "token-live-probe" not in api.text
    assert "safe-value" in html.text
    assert "safe-value" in api.text


# Тест: секреты в warnings и meta редактируются для HTML и API
def test_warning_and_meta_secrets_are_redacted_in_html_and_api() -> None:
    class SecretEnvelopeAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {"plain": "safe-value"},
                warnings=[
                    AdapterWarning(
                        code="adapter_warning",
                        message="api_key=warning-live-probe",
                    )
                ],
                meta={
                    "session": "session-live-probe",
                    "nested": {"credential": "credential-live-probe"},
                },
            )

    client = TestClient(create_beeui_app(adapter=SecretEnvelopeAdapter()))

    html = client.get("/")
    api = client.get("/api/dashboard")

    for secret in (
        "warning-live-probe",
        "session-live-probe",
        "credential-live-probe",
    ):
        assert secret not in html.text
        assert secret not in api.text
    assert "safe-value" in html.text
    assert "safe-value" in api.text


# Тест: секреты в сообщении об ошибке адаптера редактируются для HTML и API
def test_adapter_error_message_secret_is_redacted_in_html_and_api() -> None:
    class SecretErrorAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return error_result(
                "adapter_error",
                "api_key=error-live-probe",
            )

    client = TestClient(create_beeui_app(adapter=SecretErrorAdapter()))

    html = client.get("/")
    api = client.get("/api/dashboard")

    assert html.status_code == 502
    assert api.status_code == 502
    assert "error-live-probe" not in html.text
    assert "error-live-probe" not in api.text
    assert "*** REDACTED ***" in html.text
    assert "*** REDACTED ***" in api.text


# Тест: generic router не содержит импортов конкретных Bee-продуктов
def test_no_product_specific_imports_in_console_router() -> None:
    source = Path("src/beeui_module/pages/product_console.py").read_text(
        encoding="utf-8"
    )
    assert "beecap_module" not in source
    assert "beeagent_module" not in source


# Тест: адаптер с chart layout block возвращает 200 с корректным рендерингом
def test_adapter_chart_layout_block_renders() -> None:
    class ChartLayoutAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {"type": "chart", "title": "BTC/USD Chart", "width": 6},
                        {
                            "type": "metric_card",
                            "title": "Metric",
                            "value": "42",
                            "width": 6,
                        },
                    ],
                    "latest_run": {"id": "run_001", "status": "ok"},
                }
            )

    app = create_beeui_app(adapter=ChartLayoutAdapter())
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "BTC/USD Chart" in response.text
    assert "Metric" in response.text
    assert "Unsupported block type: chart" not in response.text
    assert "TemplateNotFound" not in response.text
    assert "http://" not in response.text
    assert "https://" not in response.text


# Тест: chart layout HTML экранирует опасные adapter-provided значения
def test_chart_layout_html_escapes_adapter_values() -> None:
    class UnsafeChartAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "chart",
                            "title": "<script>alert(1)</script>",
                            "subtitle": "<b>subtitle</b>",
                            "hint": "<img src=x onerror=alert(1)>",
                            "symbol": "<BTC>",
                            "timeframe": "<1h>",
                            "series": [{"name": "close", "data": [1, 2, 3]}],
                        }
                    ]
                }
            )

    response = TestClient(create_beeui_app(adapter=UnsafeChartAdapter())).get("/")

    assert response.status_code == 200
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert "&lt;b&gt;subtitle&lt;/b&gt;" in response.text
    assert "&lt;img src=x onerror=alert(1)&gt;" in response.text
    assert "&lt;BTC&gt;" in response.text
    assert "&lt;1h&gt;" in response.text
    assert "<script>alert(1)</script>" not in response.text
    assert "<img src=x onerror=alert(1)>" not in response.text


# Тест: layout[] ссылки учитывают route prefix и FastAPI mount path
def test_layout_links_use_route_prefix_and_embedded_mount() -> None:
    class LayoutAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "hero_snapshot",
                            "title": "<script>alert(1)</script>",
                            "items": [
                                {
                                    "label": "Safe run",
                                    "value": "run_safe_001",
                                    "href": "/runs/run_safe_001",
                                },
                                {
                                    "label": "Unsafe run",
                                    "value": "external",
                                    "href": "https://example.com",
                                },
                            ],
                        },
                        {
                            "type": "attention_list",
                            "title": "Attention",
                            "items": [
                                {
                                    "label": "Check",
                                    "message": "Review state",
                                    "severity": "warning",
                                }
                            ],
                        },
                    ]
                }
            )

    settings = load_settings(settings_path())
    settings["web"]["route_prefix"] = "/bee"
    prefixed_client = TestClient(
        create_beeui_app(settings=settings, adapter=LayoutAdapter())
    )
    response = prefixed_client.get("/bee/")

    assert response.status_code == 200
    for marker in (
        "page-wrapper",
        "page-header",
        "page-body",
        "container-xl",
        "row row-deck row-cards",
        "card",
        "card-header",
        "card-body",
    ):
        assert marker in response.text
    assert "row row-deck row-cards" in response.text
    assert "status-dot" in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert '<a href="/bee/runs/run_safe_001">' in response.text
    assert 'href="https://example.com"' not in response.text

    parent = FastAPI()
    mount_beeui(parent, path="/ui", adapter=LayoutAdapter())
    mounted_response = TestClient(parent).get("/ui/")

    assert mounted_response.status_code == 200
    assert '<a href="/ui/runs/run_safe_001">' in mounted_response.text


# Тест: KPI template использует responsive card grid из local CSS contract
def test_kpi_template_uses_responsive_card_grid() -> None:
    template = Path(
        "src/beeui_module/web/templates/components/layout/kpi_strip.html"
    ).read_text(encoding="utf-8")

    assert 'class="col-12 col-sm-6 col-lg-3"' in template
    assert 'class="card h-100"' in template
    assert 'class="card-body text-center"' in template
    assert 'class="col-sm"' not in template


# Тест: KPI layout title/value экранируются при реальном HTML rendering
def test_kpi_layout_html_escapes_adapter_title_and_value() -> None:
    class UnsafeKpiAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "kpi_strip",
                            "title": "<script>bad</script>",
                            "items": [
                                {
                                    "label": "Unsafe value",
                                    "value": "<script>bad</script>",
                                }
                            ],
                        }
                    ]
                }
            )

    response = TestClient(create_beeui_app(adapter=UnsafeKpiAdapter())).get("/")

    assert response.status_code == 200
    assert response.text.count("&lt;script&gt;bad&lt;/script&gt;") == 2
    assert "<script>bad</script>" not in response.text


# Тест: layout[] рендерится без ошибок при сохранении контракта API метода list_runs
def test_runs_layout_wrapper_preserves_list_api_contract() -> None:
    class LayoutRunsAdapter(FakeProductConsoleAdapter):
        def list_runs(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "metric_card",
                            "title": "Runs",
                            "value": 1,
                        }
                    ],
                    "runs": [{"id": "run_safe_001", "status": "completed"}],
                },
                meta={"count": 1},
            )

    client = TestClient(create_beeui_app(adapter=LayoutRunsAdapter()))

    html = client.get("/runs")
    api = client.get("/api/runs")

    assert html.status_code == 200
    assert "row row-deck row-cards" in html.text
    assert api.status_code == 200
    assert api.json()["data"] == [{"id": "run_safe_001", "status": "completed"}]
    assert api.json()["meta"]["count"] == 1
