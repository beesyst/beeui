from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from beeui_module.web.app import create_beeui_app


def _custom_page_schema(
    tmp_path: Path,
    custom_path: str,
    *,
    page_id: str = "custom_page",
    route_mode: str | None = None,
    page_blocks: str = "    blocks: []\n",
    extra_blocks: str = "blocks: {}\n",
    locale_block: str = "",
) -> Path:
    route_config = (
        f"    route:\n      mode: {route_mode}\n" if route_mode is not None else ""
    )
    locale_section = locale_block
    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
        f"{locale_section}"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: blue\n"
        "    base: gray\n"
        "    font: sans-serif\n"
        "    radius: 1\n"
        "    density: default\n"
        "  layout:\n"
        "    type: vertical\n"
        "    container: xl\n"
        "    sidebar:\n"
        "      variant: dark\n"
        "      collapsed: false\n"
        "    navbar:\n"
        "      enabled: true\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        f"  - title: Custom\n"
        f"    path: {custom_path}\n"
        "    icon: file\n"
        "\n"
        "data_sources: {}\n"
        f"{extra_blocks}"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
        f"  - id: {page_id}\n"
        f"    path: {custom_path}\n"
        f"{route_config}"
        "    title: Custom Page\n"
        "    subtitle: Adapter-backed\n"
        f"{page_blocks}",
        encoding="utf-8",
    )
    return schema_path


def _app_route_paths(app) -> set[str]:
    return {
        route.path
        for route in app.routes
        if isinstance(getattr(route, "path", None), str)
    }


def test_custom_adapter_page_renders_through_adapter(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class CustomPageTestAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "runs", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "metric_card",
                            "title": "Custom Metric",
                            "value": "42",
                            "width": 6,
                        },
                    ]
                }
            )

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=CustomPageTestAdapter(),
    )
    client = TestClient(app)
    response = client.get("/rop")

    assert response.status_code == 200
    assert "Custom Page" in response.text
    assert "Custom Metric" in response.text
    assert "42" in response.text


def test_data_table_page_size_footer_uses_accessible_fallback_label(
    tmp_path: Path,
) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class DataTableFooterAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            page_size = {
                "current": "25",
                "options": [
                    {"label": "25", "href": "/table?size=25", "active": True},
                    {"label": "50", "href": "/table?size=50"},
                    {"label": "100", "href": "/table?size=100"},
                ],
            }
            if query.get("labeled") == "1":
                page_size["label"] = "Rows per page"
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "data_table",
                            "title": "Records",
                            "columns": [{"key": "id", "label": "ID"}],
                            "rows": [{"id": {"label": "001"}}],
                            "pagination": {"page_size": page_size},
                        }
                    ]
                }
            )

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/table",
        page_id="table",
        locale_block="  locale:\n    default: en\n    available:\n      - en\n      - ru\n",
    )
    client = TestClient(
        create_beeui_app(
            config_path=str(ui_cfg_path),
            adapter=DataTableFooterAdapter(),
        )
    )

    english = client.get("/table")
    russian = client.get("/table?lang=ru")
    labeled = client.get("/table?labeled=1")

    assert english.status_code == 200
    assert russian.status_code == 200
    assert labeled.status_code == 200
    assert ">Show<" not in english.text
    assert ">Показать<" not in russian.text
    assert 'aria-label="Show entries"' in english.text
    assert 'aria-label="Показать записей"' in russian.text
    assert "data-beeui-page-size-select" in english.text
    assert '<option value="/table?size=25" selected>25</option>' in english.text
    assert '<option value="/table?size=50">50</option>' in english.text
    assert '<option value="/table?size=100">100</option>' in english.text
    assert "Rows per page" in labeled.text
    assert 'aria-label="Rows per page"' in labeled.text


def test_custom_adapter_page_receives_lang_from_cookie(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    seen: list[dict[str, str]] = []

    class CookieLangAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "runs", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            seen.append(dict(query))
            return ok_result({"layout": []})

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/rop",
        page_id="rop",
        locale_block=(
            "  locale:\n    default: en\n    available:\n      - en\n      - ru\n"
        ),
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=CookieLangAdapter(),
    )
    client = TestClient(app)
    client.cookies.set("beeui_lang", "ru")
    response = client.get("/rop")

    assert response.status_code == 200
    assert seen and seen[0].get("lang") == "ru"


def test_custom_adapter_page_lang_query_overrides_cookie(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    seen: list[dict[str, str]] = []

    class QueryLangAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "runs", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            seen.append(dict(query))
            return ok_result({"layout": []})

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/rop",
        page_id="rop",
        locale_block=(
            "  locale:\n    default: en\n    available:\n      - en\n      - ru\n"
        ),
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=QueryLangAdapter(),
    )
    client = TestClient(app)
    client.cookies.set("beeui_lang", "ru")
    response = client.get("/rop?lang=en")

    assert response.status_code == 200
    assert seen and seen[0].get("lang") == "en"


def test_custom_adapter_page_unavailable_degraded(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, error_result, ok_result
    from beeui_module.web.app import create_beeui_app

    class DegradedPageTestAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            return error_result("unavailable", f"Page {page_id} is not available")

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=DegradedPageTestAdapter(),
    )
    client = TestClient(app)
    response = client.get("/rop")

    assert response.status_code in (200, 503)
    assert "Custom Page" in response.text


def test_custom_page_get_does_not_mutate_config(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class NoCustomPagesAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    original_content = ui_cfg_path.read_text(encoding="utf-8")

    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=NoCustomPagesAdapter(),
    )
    client = TestClient(app)
    client.get("/rop")

    assert ui_cfg_path.read_text(encoding="utf-8") == original_content


def test_custom_adapter_page_malformed_payload_degrades(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class MalformedPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            return ok_result(["bad"])

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=MalformedPageAdapter(),
    )
    client = TestClient(app)

    response = client.get("/rop")

    assert response.status_code == 502
    assert "Adapter returned malformed payload" in response.text


def test_custom_adapter_page_redacts_payload_before_render(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class RedactedPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "data_table",
                            "title": "Sources",
                            "columns": [
                                {"key": "name", "label": "Name"},
                                {"key": "masked_value", "label": "Password"},
                                {"key": "actions", "label": "", "cell": "actions"},
                            ],
                            "rows": [
                                {
                                    "name": {"label": "Synthetic mailbox"},
                                    "masked_value": {"label": "********"},
                                    "password": "synthetic-secret",
                                    "actions": [
                                        {
                                            "action_id": "source_add",
                                            "label": "Add",
                                            "flow": "direct_execute",
                                            "fields": [
                                                {
                                                    "name": "password",
                                                    "type": "password",
                                                    "label": "Password",
                                                    "required": True,
                                                    "max_length": 128,
                                                    "value": "",
                                                }
                                            ],
                                        },
                                        {
                                            "action_id": "source_update",
                                            "label": "Edit",
                                            "flow": "direct_execute",
                                            "fields": [
                                                {
                                                    "name": "password",
                                                    "type": "password",
                                                    "label": "Password",
                                                    "required": False,
                                                    "max_length": 128,
                                                    "value": "",
                                                }
                                            ],
                                        },
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "raw_json_panel",
                            "title": "Debug",
                            "data": {"api_key": "secret-value"},
                        },
                    ]
                }
            )

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=RedactedPageAdapter(),
    )
    response = TestClient(app).get("/rop")
    html = response.text

    assert response.status_code == 200
    assert "secret-value" not in html
    assert "synthetic-secret" not in html
    assert "*** REDACTED ***" in html
    assert "Synthetic mailbox" in html
    assert "********" in html
    assert 'data-beeui-column-key="masked_value"' in html
    assert 'data-beeui-column-key="password"' not in html
    assert "Add" in html
    assert "Edit" in html
    assert '"name": "password"' in html
    assert '"type": "password"' in html
    assert '"label": "Password"' in html


def test_custom_route_rop_registers_with_adapter(tmp_path: Path) -> None:
    from fastapi import FastAPI

    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import mount_beeui

    class RopPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "filter_form",
                            "title": "Filters",
                            "actions": {
                                "apply": {
                                    "href": "https://invalid.example/apply",
                                    "label": "Apply",
                                },
                                "reset": {"href": "/rop?reset=1", "label": "Reset"},
                            },
                            "columns_toggle_href": "/rop?columns=1",
                            "columns_open": True,
                            "column_toggles": [
                                {
                                    "key": "state",
                                    "label": "State",
                                    "visible": True,
                                    "toggle_href": "/rop?column=state",
                                }
                            ],
                            "fields": [
                                {
                                    "type": "checkboxes",
                                    "name": "state",
                                    "choices": [
                                        {
                                            "value": "ok",
                                            "label": "OK",
                                            "toggle_href": "/rop?state=ok",
                                        },
                                        {
                                            "value": "bad",
                                            "label": "Bad",
                                            "toggle_href": "https://invalid.example",
                                        },
                                    ],
                                }
                            ],
                        },
                        {
                            "type": "data_table",
                            "title": "ROP",
                            "columns": [
                                {
                                    "key": "run",
                                    "label": "Run",
                                    "sortable": True,
                                    "sort_href": "/rop?sort=run",
                                    "sort_active": True,
                                    "sort_direction": "asc",
                                }
                            ],
                            "rows": [{"run": "42"}],
                        },
                    ]
                }
            )

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/rop",
        page_blocks=(
            "    tabs:\n"
            "      active_param: tab\n"
            "      items:\n"
            "        - id: overview\n"
            "          title: Overview\n"
            "          href: /rop?tab=overview\n"
            "    blocks: []\n"
        ),
    )
    ui_cfg_path.write_text(
        ui_cfg_path.read_text(encoding="utf-8").replace(
            "  layout:\n",
            "  locale:\n    default: en\n    available:\n      - en\n      - ru\n  layout:\n",
            1,
        ),
        encoding="utf-8",
    )
    parent = FastAPI()
    mount_beeui(
        parent,
        path="/ui",
        config_path=str(ui_cfg_path),
        adapter=RopPageAdapter(),
    )
    client = TestClient(parent)

    response = client.get("/ui/rop")
    assert response.status_code == 200
    assert "ROP" in response.text
    assert "42" in response.text
    assert 'action="/ui/rop"' in response.text
    assert 'method="GET"' in response.text
    assert ">Apply</button>" in response.text
    assert 'href="/ui/rop?reset=1"' in response.text
    assert 'href="/ui/rop?column=state"' in response.text
    assert 'href="/ui/rop?state=ok"' in response.text
    assert 'href="/ui/rop?sort=run"' in response.text
    assert 'aria-sort="ascending"' in response.text
    assert 'class="table-sort asc"' in response.text
    assert 'href="/ui/static/css/beeui.css?v=21"' in response.text
    assert 'href="/ui/"' in response.text
    assert 'href="/ui/rop?lang=ru"' in response.text
    assert 'href="/ui/rop?tab=overview"' in response.text
    assert "/ui/ui/" not in response.text
    assert "invalid.example" not in response.text


@pytest.mark.parametrize("path", ["/venues/mrkt", "/venues/binance"])
def test_metadata_route_venues_skipped(tmp_path: Path, path: str) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result

    class VenuePageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

    app = create_beeui_app(
        config_path=str(_custom_page_schema(tmp_path, path, route_mode="metadata")),
        adapter=VenuePageAdapter(),
    )
    assert path not in _app_route_paths(app)
    assert "/venues/{venue_id}" in _app_route_paths(app)

    response = TestClient(app).get(path)
    assert response.status_code == 503
    assert "Custom Page" not in response.text


def test_metadata_route_runs_skipped(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class RunsPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/runs/run_001",
        route_mode="metadata",
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=RunsPageAdapter(),
    )
    route_paths = _app_route_paths(app)
    assert "/runs/run_001" not in route_paths
    assert "/runs/{run_id}" in route_paths

    client = TestClient(app)

    response = client.get("/runs/run_001")
    assert response.status_code == 200
    assert "Custom Page" not in response.text
    assert "Run run_001" in response.text or "run_001" in response.text


def test_adapter_route_hidra_binance_registers(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class HidraPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )
            self.page_calls = []

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            self.page_calls.append((page_id, dict(query)))
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "metric_card",
                            "title": "Hidra Adapter",
                            "value": page_id,
                        }
                    ]
                }
            )

    adapter = HidraPageAdapter()
    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/hidra/binance",
        page_id="hidra_binance",
        route_mode="adapter",
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=adapter,
    )

    route_paths = _app_route_paths(app)
    assert "/hidra/binance" in route_paths

    client = TestClient(app)
    response = client.get("/hidra/binance?tab=orders")
    assert response.status_code == 200
    assert "Hidra Adapter" in response.text
    assert adapter.page_calls == [("hidra_binance", {"tab": "orders"})]


def test_configured_route_likes_top_registers_without_adapter_get_page(
    tmp_path: Path,
) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class LikesPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )
            self.page_calls = []

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            self.page_calls.append(page_id)
            return ok_result({})

    adapter = LikesPageAdapter()
    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/likes/top",
        page_id="likes_top",
        route_mode="configured",
        extra_blocks=(
            "blocks:\n"
            "  likes_metric:\n"
            "    type: metric_card\n"
            "    title: Likes Metric\n"
            '    value: "99"\n'
        ),
        page_blocks="    blocks:\n      - block: likes_metric\n",
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=adapter,
    )

    route_paths = _app_route_paths(app)
    assert "/likes/top" in route_paths

    client = TestClient(app)
    response = client.get("/likes/top")
    assert response.status_code == 200
    assert "Likes Metric" in response.text
    assert "99" in response.text
    assert adapter.page_calls == []


@pytest.mark.parametrize(
    ("route_mode", "registered"),
    [("adapter", True), ("metadata", False)],
)
def test_modes_live_route_mode(
    tmp_path: Path, route_mode: str, registered: bool
) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result

    class ModesPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            return ok_result(
                {"layout": [{"type": "metric_card", "title": "Mode", "value": page_id}]}
            )

    app = create_beeui_app(
        config_path=str(
            _custom_page_schema(tmp_path, "/modes/live", route_mode=route_mode)
        ),
        adapter=ModesPageAdapter(),
    )
    assert ("/modes/live" in _app_route_paths(app)) is registered
    if registered:
        response = TestClient(app).get("/modes/live")
        assert response.status_code == 200
        assert "Mode" in response.text


def test_custom_route_system_paths_skipped(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class SystemPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

    for path in (
        "/api/debug",
        "/auth/test",
        "/static/test",
        "/components/test",
        "/health",
    ):
        ui_cfg_path = _custom_page_schema(tmp_path, path)
        app = create_beeui_app(
            config_path=str(ui_cfg_path),
            adapter=SystemPageAdapter(),
        )
        route_paths = _app_route_paths(app)
        client = TestClient(app)
        response = client.get(path)
        if path == "/health":
            assert path in route_paths
            assert response.status_code == 200
            assert response.json().get("app") == "beeui"
        else:
            assert path not in route_paths
            assert response.status_code in {404, 405}


def test_adapter_custom_pages_use_navigation_visibility_resolver(
    tmp_path: Path,
) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result

    class VisibilityPageAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard", "runs", "custom_pages"),
                )
            )

        def get_dashboard(self):
            return ok_result({})

        def list_runs(self):
            return ok_result([])

        def get_run(self, run_id):
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id):
            return ok_result([])

        def read_artifact(self, run_id, artifact_id):
            return ok_result({})

        def get_config_read_model(self):
            return ok_result({})

        def get_page(self, page_id, query):
            return ok_result(
                {
                    "layout": [
                        {
                            "type": "metric_card",
                            "title": "Custom Metric",
                            "value": "42",
                            "width": 6,
                        },
                    ]
                }
            )

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=VisibilityPageAdapter(),
        navigation_visibility_resolver=lambda request, path: path != "/rop",
    )
    client = TestClient(app)

    response = client.get("/rop")
    assert response.status_code == 200
    assert "Custom Metric" in response.text
    assert 'href="/rop"' not in response.text
    assert 'href="/"' in response.text
