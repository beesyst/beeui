from __future__ import annotations

import re
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


def test_adapter_dashboard_uses_page_body_container_wrapper() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    body_idx = response.text.index('class="page-body"')
    container_idx = response.text.index("container-xl", body_idx)
    assert container_idx > body_idx


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


def test_demo_mode_still_uses_configured_pages_without_adapter() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Demo operator dashboard" in response.text
    assert client.get("/api/dashboard").status_code == 404


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


def test_html_escapes_adapter_values() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert '<img src=x onerror="alert(1)">' not in response.text
    assert "\\u003cimg" in response.text or "&lt;img" in response.text


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


def test_no_product_specific_imports_in_console_router() -> None:
    source = Path("src/beeui_module/pages/product_console.py").read_text(
        encoding="utf-8"
    )
    assert "beecap_module" not in source
    assert "beeagent_module" not in source


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
    assert "<script>alert(1)</script>" not in response.text
    assert "<img src=x onerror=alert(1)>" not in response.text


def test_chart_layout_html_uses_safe_json_script_config() -> None:
    class UnsafeChartConfigAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "chart",
                            "title": "Safe chart config",
                            "series": [
                                {
                                    "name": 'A <script>x</script> "quote"',
                                    "data": [1, 2, 3],
                                }
                            ],
                        }
                    ]
                }
            )

    response = TestClient(create_beeui_app(adapter=UnsafeChartConfigAdapter())).get("/")

    assert response.status_code == 200
    assert "<script>x</script>" not in response.text
    assert 'type="application/json"' in response.text
    assert "beeui-chart-config" in response.text
    assert 'data-chart-config="{' not in response.text
    assert "|safe" not in response.text
    assert "\\u003cscript\\u003ex\\u003c/script\\u003e" in response.text


def test_chart_templates_do_not_use_unsafe_serialization() -> None:
    template_root = Path("src/beeui_module/web/templates")
    chart = (template_root / "components/layout/chart.html").read_text(encoding="utf-8")
    base = (template_root / "base.html").read_text(encoding="utf-8")

    assert "|safe" not in chart
    assert 'data-chart-config="{{' not in chart
    assert "innerHTML" not in base


def test_nested_chart_in_group_loads_chart_asset() -> None:
    class NestedChartAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "group",
                            "children": [
                                {
                                    "type": "chart",
                                    "title": "Nested chart",
                                    "series": [{"name": "x", "data": [1, 2, 3]}],
                                }
                            ],
                        }
                    ]
                }
            )

    response = TestClient(create_beeui_app(adapter=NestedChartAdapter())).get("/")

    assert response.status_code == 200
    assert "beeui-chart-container" in response.text
    assert "/static/vendor/apexcharts/apexcharts.min.js" in response.text


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


def test_data_table_links_use_route_prefix_and_embedded_mount() -> None:
    class DataTableAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "data_table",
                            "title": "Runs",
                            "toolbar": {
                                "actions": [
                                    {"label": "All runs", "href": "/runs"},
                                ]
                            },
                            "columns": [
                                {"key": "run", "label": "Run", "cell": "link"},
                                {"key": "actions", "label": "", "cell": "actions"},
                            ],
                            "rows": [
                                {
                                    "run": {
                                        "label": "Open run",
                                        "href": "/runs/run_safe_001",
                                    },
                                    "actions": [
                                        {
                                            "label": "Edit",
                                            "href": "/runs/run_safe_001/edit",
                                        }
                                    ],
                                }
                            ],
                            "pagination": {
                                "label": "Showing 1 to 1 of 2 entries",
                                "pages": [
                                    {
                                        "label": "2",
                                        "href": "/runs?page=2",
                                    }
                                ],
                            },
                        }
                    ]
                }
            )

    settings = load_settings(settings_path())
    settings["web"]["route_prefix"] = "/bee"
    prefixed_response = TestClient(
        create_beeui_app(settings=settings, adapter=DataTableAdapter())
    ).get("/bee/")

    assert prefixed_response.status_code == 200
    assert 'href="/bee/runs"' in prefixed_response.text
    assert '<a href="/bee/runs/run_safe_001">Open run</a>' in prefixed_response.text
    assert 'href="/bee/runs/run_safe_001/edit"' in prefixed_response.text
    assert 'href="/bee/runs?page=2"' in prefixed_response.text

    parent = FastAPI()
    mount_beeui(parent, path="/ui", adapter=DataTableAdapter())
    mounted_response = TestClient(parent).get("/ui/")

    assert mounted_response.status_code == 200
    assert 'href="/ui/runs"' in mounted_response.text
    assert '<a href="/ui/runs/run_safe_001">Open run</a>' in mounted_response.text
    assert 'href="/ui/runs/run_safe_001/edit"' in mounted_response.text
    assert 'href="/ui/runs?page=2"' in mounted_response.text


def test_kpi_template_uses_responsive_card_grid() -> None:
    template = Path(
        "src/beeui_module/web/templates/components/layout/kpi_strip.html"
    ).read_text(encoding="utf-8")

    assert 'class="col-12 col-sm-6 col-lg-3"' in template
    assert 'class="card h-100"' in template
    assert 'class="card-body text-center"' in template
    assert 'class="col-sm"' not in template


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


def test_operator_hero_block_renders_through_layout() -> None:
    class NewBlocksAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "operator_hero",
                            "title": "System Snapshot",
                            "subtitle": "Runtime: stopped",
                            "status": "ok",
                            "width": 12,
                            "items": [
                                {
                                    "label": "Latest run",
                                    "value": "run_001",
                                    "href": "/runs/run_001",
                                },
                                {"label": "Runtime", "value": "stopped"},
                            ],
                            "primary_links": [
                                {
                                    "label": "Open latest run",
                                    "href": "/runs/run_001",
                                }
                            ],
                        },
                        {
                            "type": "venue_card",
                            "title": "MRKT",
                            "subtitle": "Live monitoring",
                            "status": "degraded",
                            "width": 6,
                            "items": [
                                {"label": "Health", "value": "ok", "status": "ok"},
                            ],
                            "alerts": [
                                {
                                    "severity": "warning",
                                    "message": "Profit unavailable",
                                }
                            ],
                            "links": [
                                {"label": "Open venue", "href": "/venues/mrkt"},
                            ],
                        },
                        {
                            "type": "kpi_grid",
                            "title": "KPI",
                            "width": 12,
                            "items": [
                                {
                                    "label": "Health",
                                    "value": "ok",
                                    "status": "ok",
                                }
                            ],
                        },
                        {
                            "type": "state_grid",
                            "title": "Current State",
                            "width": 12,
                            "items": [
                                {"label": "Health", "value": "ok", "status": "ok"},
                                {"label": "Tick", "value": "5 / 5"},
                            ],
                        },
                        {
                            "type": "quick_links",
                            "title": "Quick Links",
                            "width": 12,
                            "items": [
                                {
                                    "label": "Latest Run Detail",
                                    "href": "/runs/run_001",
                                },
                                {"label": "All Runs", "href": "/runs"},
                            ],
                        },
                        {
                            "type": "run_table",
                            "title": "Recent Runs",
                            "width": 12,
                            "columns": [
                                "Run",
                                "Mode",
                                "Venue",
                                "Symbol",
                                "TF",
                                "Started UTC",
                                "Health",
                                "Event Time UTC",
                                "Event",
                                "Severity",
                                "Events",
                                "Artifact",
                            ],
                            "rows": [
                                {
                                    "run_id": "run_001",
                                    "run_href": "/runs/run_001",
                                    "mode": "live",
                                    "venue": "mrkt",
                                    "symbol": "TONNFT",
                                    "timeframe": "1m",
                                    "started_utc": "2026-06-05 04:34:54",
                                    "health": "ok",
                                    "event_time_utc": "2026-06-05 04:35:36",
                                    "event": "venues/mrkt/lifecycle",
                                    "severity": "info",
                                    "events": "9",
                                    "artifact": "lifecycle.jsonl",
                                    "artifact_href": "/runs/run_001/artifacts/lifecycle_jsonl",
                                }
                            ],
                            "filters": True,
                        },
                    ]
                }
            )

    response = TestClient(create_beeui_app(adapter=NewBlocksAdapter())).get("/")

    assert response.status_code == 200
    for marker in (
        "System Snapshot",
        "Runtime: stopped",
        "Open latest run",
        "MRKT",
        "Live monitoring",
        "degraded",
        "Profit unavailable",
        "Open venue",
        "KPI",
        "Health",
        "Current State",
        "Quick Links",
        "Latest Run Detail",
        "All Runs",
        "Recent Runs",
        "run_001",
        "lifecycle.jsonl",
    ):
        assert marker in response.text

    for forbidden in (
        "http://",
        "https://",
        "None",
        "&lt;None&gt;",
        "undefined",
    ):
        assert forbidden not in response.text


def test_new_blocks_escape_unsafe_adapter_values() -> None:
    class UnsafeNewBlocksAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "operator_hero",
                            "title": "<script>bad</script>",
                            "width": 12,
                            "items": [
                                {
                                    "label": "<b>label</b>",
                                    "value": "<i>value</i>",
                                }
                            ],
                            "primary_links": [
                                {
                                    "label": "<script>link</script>",
                                    "href": "/runs/safe",
                                }
                            ],
                        },
                        {
                            "type": "venue_card",
                            "title": "Venue",
                            "width": 6,
                            "items": [
                                {
                                    "label": "Health",
                                    "value": "<script>alert(1)</script>",
                                }
                            ],
                            "alerts": [
                                {
                                    "severity": "error",
                                    "message": "<img src=x onerror=alert(1)>",
                                }
                            ],
                        },
                        {
                            "type": "kpi_grid",
                            "title": "KPI",
                            "width": 12,
                            "items": [
                                {
                                    "label": "<script>kpi</script>",
                                    "value": "42",
                                }
                            ],
                        },
                        {
                            "type": "quick_links",
                            "title": "Links",
                            "width": 12,
                            "items": [
                                {
                                    "label": "<script>link</script>",
                                    "href": "/runs/safe",
                                }
                            ],
                        },
                        {
                            "type": "run_table",
                            "title": "Runs",
                            "width": 12,
                            "columns": [
                                "Run",
                                "Mode",
                                "Venue",
                                "Symbol",
                                "TF",
                                "Started UTC",
                                "Health",
                                "Event Time UTC",
                                "Event",
                                "Severity",
                                "Events",
                                "Artifact",
                            ],
                            "rows": [
                                {
                                    "run_id": "<script>id</script>",
                                    "run_href": "/runs/safe",
                                    "mode": "<script>mode</script>",
                                    "venue": "",
                                    "symbol": "",
                                    "timeframe": "",
                                    "started_utc": "",
                                    "health": "",
                                    "event_time_utc": "",
                                    "event": "",
                                    "severity": "",
                                    "events": "",
                                    "artifact": "<script>artifact</script>",
                                    "artifact_href": "/runs/artifact",
                                }
                            ],
                        },
                    ]
                }
            )

    response = TestClient(create_beeui_app(adapter=UnsafeNewBlocksAdapter())).get("/")

    assert response.status_code == 200
    assert "<script>bad</script>" not in response.text
    assert "<b>label</b>" not in response.text
    assert "<i>value</i>" not in response.text
    assert "<script>link</script>" not in response.text
    assert "<script>alert(1)</script>" not in response.text
    assert "<img src=x onerror=alert(1)>" not in response.text
    assert "<script>kpi</script>" not in response.text
    assert "<script>id</script>" not in response.text
    assert "<script>mode</script>" not in response.text
    assert "<script>artifact</script>" not in response.text
    assert "&lt;script&gt;" in response.text
    assert "&lt;b&gt;label&lt;/b&gt;" in response.text
    assert "&lt;i&gt;value&lt;/i&gt;" in response.text


def test_new_blocks_have_no_external_links() -> None:
    class ExternalLinkAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "operator_hero",
                            "title": "Test",
                            "width": 12,
                            "items": [
                                {
                                    "label": "Bad",
                                    "value": "ext",
                                    "href": "http://evil.com",
                                },
                                {"label": "Good", "value": "int", "href": "/runs/1"},
                            ],
                            "primary_links": [
                                {
                                    "label": "Bad link",
                                    "href": "https://evil.com",
                                },
                                {"label": "Good link", "href": "/runs/2"},
                            ],
                        },
                        {
                            "type": "venue_card",
                            "title": "Venue",
                            "width": 6,
                            "links": [
                                {
                                    "label": "Bad",
                                    "href": "//evil.com",
                                },
                                {"label": "Good", "href": "/venues/mrkt"},
                            ],
                        },
                        {
                            "type": "quick_links",
                            "title": "Links",
                            "width": 12,
                            "items": [
                                {"label": "Safe", "href": "/runs/1"},
                                {"label": "Evil", "href": "http://evil.com"},
                            ],
                        },
                    ]
                }
            )

    response = TestClient(create_beeui_app(adapter=ExternalLinkAdapter())).get("/")

    assert response.status_code == 200
    assert 'href="http://evil.com"' not in response.text
    assert 'href="https://evil.com"' not in response.text
    assert 'href="//evil.com"' not in response.text
    assert "/runs/1" in response.text
    assert "/runs/2" in response.text
    assert "/venues/mrkt" in response.text


def test_new_block_templates_no_external_refs() -> None:
    template_root = Path("src/beeui_module/web/templates/components/layout")
    for name in (
        "operator_hero.html",
        "venue_card.html",
        "kpi_grid.html",
        "state_grid.html",
        "quick_links.html",
        "run_table.html",
        "group.html",
    ):
        content = (template_root / name).read_text(encoding="utf-8").lower()
        assert "cdn.jsdelivr" not in content, f"{name} contains cdn.jsdelivr"
        assert "posthog" not in content, f"{name} contains posthog"
        assert "scripts.tabler.io" not in content, f"{name} contains scripts.tabler.io"
        assert "preview.tabler.io" not in content, f"{name} contains preview.tabler.io"
        assert "docs.tabler.io" not in content, f"{name} contains docs.tabler.io"
        assert "http://" not in content, f"{name} contains http://"
        assert "https://" not in content, f"{name} contains https://"
        assert "|safe" not in content, f"{name} contains |safe"


def test_accordion_renders_chevron_toggle_svg() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="accordion-button-toggle"' in response.text
    assert 'aria-hidden="true"' in response.text
    assert '<path d="M6 9l6 6l6 -6" />' in response.text
    assert 'data-bs-toggle="collapse"' in response.text
    assert 'aria-expanded="false"' in response.text


def test_accordion_uses_tabler_div_header_markup() -> None:
    app = create_beeui_app(adapter=FakeProductConsoleAdapter())
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert '<div class="accordion-header"' in response.text
    assert '<h2 class="accordion-header"' not in response.text


def test_accordion_variant_tabs_renders_tabs_class(tmp_path: Path) -> None:
    from beeui_module.pages.config import load_beeui_config

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        Path("config/schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "data_sources:\n  demo_dashboard:\n    type: demo\n\n",
            "components:\n  accordion:\n    variant: tabs\n\ndata_sources:\n  demo_dashboard:\n    type: demo\n\n",
            1,
        ),
        encoding="utf-8",
    )
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(schema_path)
    app = create_beeui_app(
        settings=settings, ui_config=ui_config, adapter=FakeProductConsoleAdapter()
    )
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="accordion accordion-tabs"' in response.text


def test_accordion_variant_inverted_plus_renders_plus_svg(tmp_path: Path) -> None:
    from beeui_module.pages.config import load_beeui_config

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        Path("config/schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "data_sources:\n  demo_dashboard:\n    type: demo\n\n",
            "components:\n  accordion:\n    variant: inverted_plus\n\ndata_sources:\n  demo_dashboard:\n    type: demo\n\n",
            1,
        ),
        encoding="utf-8",
    )
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(schema_path)
    app = create_beeui_app(
        settings=settings, ui_config=ui_config, adapter=FakeProductConsoleAdapter()
    )
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "accordion-plus" in response.text
    assert "accordion-button-toggle-plus" in response.text
    assert '<path d="M12 5l0 14" />' in response.text
    assert '<path d="M5 12l14 0" />' in response.text


def test_accordion_variant_icons_renders_icon_and_chevron(tmp_path: Path) -> None:
    from beeui_module.pages.config import load_beeui_config

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        Path("config/schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "data_sources:\n  demo_dashboard:\n    type: demo\n\n",
            "components:\n  accordion:\n    variant: icons\n\ndata_sources:\n  demo_dashboard:\n    type: demo\n\n",
            1,
        ),
        encoding="utf-8",
    )
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(schema_path)
    app = create_beeui_app(
        settings=settings, ui_config=ui_config, adapter=FakeProductConsoleAdapter()
    )
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="accordion-button-icon"' in response.text
    assert 'class="accordion-button-toggle"' in response.text


def test_no_external_refs_in_affected_templates() -> None:
    template_root = Path("src/beeui_module/web/templates")
    affected = [
        "page.html",
        "product_dashboard.html",
        "components/primitives/catalog_primitives.html",
    ]
    for name in affected:
        content = (template_root / name).read_text(encoding="utf-8").lower()
        assert "cdn.jsdelivr" not in content, f"{name} contains cdn.jsdelivr"
        assert "posthog" not in content, f"{name} contains posthog"
        assert "scripts.tabler.io" not in content, f"{name} contains scripts.tabler.io"
        assert "preview.tabler.io" not in content, f"{name} contains preview.tabler.io"
        assert "docs.tabler.io" not in content, f"{name} contains docs.tabler.io"
        http_refs = re.findall(r"http://[^\s\"'>]+", content)
        svg_ns_only = all(ref == "http://www.w3.org/2000/svg" for ref in http_refs)
        if not svg_ns_only:
            assert False, f"{name} contains non-SVG http:// references: {http_refs}"
        assert "|safe" not in content, f"{name} contains |safe"


def test_layout_group_renders_through_adapter() -> None:
    class GroupLayoutAdapter(FakeProductConsoleAdapter):
        def get_dashboard(self) -> Any:
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "group",
                            "width": 6,
                            "direction": "vertical",
                            "children": [
                                {
                                    "type": "metric_card",
                                    "title": "Storage",
                                    "value": "42",
                                    "width": 12,
                                },
                                {
                                    "type": "metric_card",
                                    "title": "Activity Feed",
                                    "value": "active",
                                    "width": 12,
                                },
                            ],
                        },
                        {
                            "type": "metric_card",
                            "title": "Development Activity",
                            "value": "high",
                            "width": 6,
                        },
                    ],
                    "latest_run": {"id": "run_001", "status": "ok"},
                }
            )

    response = TestClient(create_beeui_app(adapter=GroupLayoutAdapter())).get("/")

    assert response.status_code == 200
    assert "Storage" in response.text
    assert "Activity Feed" in response.text
    assert "Development Activity" in response.text
    assert "row row-cards" in response.text
    assert "http://" not in response.text
    assert "https://" not in response.text


def test_no_product_imports_in_affected_source() -> None:
    source_root = Path("src/beeui_module")
    affected = [
        "pages/router.py",
        "pages/product_console.py",
        "blocks/layout_renderer.py",
    ]
    for name in affected:
        content = (source_root / name).read_text(encoding="utf-8")
        for product_module in ("beecap_module", "beeagent_module"):
            assert product_module not in content, f"{name} contains {product_module}"


def test_adapter_dashboard_navigation_follows_locale() -> None:
    from beeui_module.pages.config import load_beeui_config
    from beeui_module.pages.models import LocaleConfig

    adapter = FakeProductConsoleAdapter()
    settings = load_settings(settings_path())
    settings["product"]["title"] = "Fake"
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    from dataclasses import replace

    ui_config = replace(
        ui_config,
        locale=LocaleConfig(default="en", available=("en", "ru")),
        navigation=[
            replace(n, title={"en": "Dashboard", "ru": "Дашборд"})
            for n in ui_config.navigation
        ],
    )

    app = create_beeui_app(settings=settings, ui_config=ui_config, adapter=adapter)
    client = TestClient(app)

    ru = client.get("/?lang=ru")
    assert ru.status_code == 200
    assert "Дашборд" in ru.text
    assert "lang=ru" in ru.text

    en = client.get("/")
    assert en.status_code == 200
    assert "Dashboard" in en.text
    assert "?lang=" not in en.text  # no lang param in nav links when default locale
