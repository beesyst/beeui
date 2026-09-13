from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.pages.config import load_beeui_config
from beeui_module.web.app import create_beeui_app


def test_configured_pages_render_from_yaml() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    root = client.get("/")
    runs = client.get("/runs")

    assert root.status_code == 200
    assert "Dashboard" in root.text
    assert "Demo operator dashboard" in root.text
    assert "Workspace" in root.text
    assert "Reports" in root.text

    assert runs.status_code == 200
    assert "Runs" in runs.text
    assert "Placeholder page for future run overview" in runs.text


def test_active_navigation_item_is_rendered() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/runs")

    assert response.status_code == 200
    assert 'href="/runs"' in response.text
    assert 'href="/"' in response.text
    assert "sidebar__link is-active" in response.text
    assert "beeui-nav-group-title" in response.text
    assert "beeui-nav-children" in response.text


def test_disabled_navigation_item_is_rendered_safely() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'aria-disabled="true"' in response.text
    assert "beeui-nav-disabled" in response.text


def test_unknown_page_returns_404() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/missing")

    assert response.status_code == 404


def test_config_provided_page_strings_are_escaped(tmp_path: Path) -> None:
    settings = load_settings(settings_path())

    ui_cfg_path = tmp_path / "schema.yml"
    ui_cfg_path.write_text(
        "app:\n"
        "  title: BeeUI Demo\n"
        "  product: demo\n"
        "  logo_text: BeeUI\n"
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
        "  - title: Workspace\n"
        "    children:\n"
        '      - title: "<script>alert(1)</script>"\n'
        "        path: /\n"
        "        icon: dashboard\n"
        "      - title: Runs\n"
        "        path: /runs\n"
        "        icon: list\n"
        "\n"
        "blocks:\n"
        "  latest_run:\n"
        "    type: metric_card\n"
        "    title: Latest\n"
        '    value: "<script>alert(9)</script>"\n'
        "\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        '    title: "<script>alert(1)</script>"\n'
        '    subtitle: "<script>alert(2)</script>"\n'
        "    blocks:\n"
        "      - block: latest_run\n"
        "        width: 6\n"
        "  - id: runs\n"
        "    path: /runs\n"
        "    title: Runs\n"
        "    subtitle: Placeholder page for future run overview\n"
        "    blocks: []\n",
        encoding="utf-8",
    )

    ui_config = load_beeui_config(ui_cfg_path)
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in response.text
    assert "<script>alert(2)</script>" not in response.text
    assert "<script>alert(9)</script>" not in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in response.text
    assert "&lt;script&gt;alert(9)&lt;/script&gt;" in response.text


def test_empty_state_component_is_rendered() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/runs")

    assert response.status_code == 200
    assert "No blocks configured" in response.text
    assert (
        "Add block placements in config/schema.yml to render dashboard cards."
        in response.text
    )


def test_dashboard_blocks_are_rendered_from_schema() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Latest Run" in response.text
    assert "Runtime" in response.text
    assert "Session KPIs" in response.text
    assert "Recent runs" in response.text
    assert "Quick links" in response.text
    assert "Demo mode" in response.text
    assert "Summary" in response.text
    assert "Bootstrap progress" in response.text
    assert "<progress" in response.text
    assert 'style="' not in response.text


def test_block_non_normal_states_are_rendered(tmp_path: Path) -> None:
    settings = load_settings(settings_path())

    ui_cfg_path = tmp_path / "schema.yml"
    ui_cfg_path.write_text(
        (settings_path().parent / "schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  runtime_status:\n    type: status_card\n    title: Runtime\n",
            "  runtime_status:\n    type: status_card\n    title: Runtime\n    state: degraded\n",
            1,
        )
        .replace(
            "  notice:\n    type: alert_card\n    title: Demo mode\n",
            "  notice:\n    type: alert_card\n    title: Demo mode\n    state: error\n",
            1,
        ),
        encoding="utf-8",
    )

    ui_config = load_beeui_config(ui_cfg_path)
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "beeui-block-state-degraded" in response.text
    assert "Block state: degraded" in response.text
    assert ">error</span>" in response.text


def test_resolver_missing_selector_renders_degraded_block_state(tmp_path: Path) -> None:
    settings = load_settings(settings_path())

    ui_cfg_path = tmp_path / "schema.yml"
    ui_cfg_path.write_text(
        (settings_path().parent / "schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    value_selector: dashboard.latest_run.id\n",
            "    value_selector: dashboard.latest_run.missing\n",
            1,
        ),
        encoding="utf-8",
    )

    ui_config = load_beeui_config(ui_cfg_path)
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "beeui-block-state-degraded" in response.text
    assert "Unavailable" in response.text


def test_resolver_invalid_table_rows_render_error_state(tmp_path: Path) -> None:
    settings = load_settings(settings_path())

    ui_cfg_path = tmp_path / "schema.yml"
    ui_cfg_path.write_text(
        (settings_path().parent / "schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "    rows_selector: runs\n",
            "    rows_selector: dashboard.latest_run.id\n",
            1,
        ),
        encoding="utf-8",
    )

    ui_config = load_beeui_config(ui_cfg_path)
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Recent runs" in response.text
    assert "beeui-block-state-error" in response.text
    assert "Resolved data is unavailable." in response.text


def test_resolved_static_values_are_escaped(tmp_path: Path) -> None:
    settings = load_settings(settings_path())
    fixture_path = Path("tests/fixtures/demo_static/dashboard_unsafe.json")

    ui_cfg_path = tmp_path / "schema.yml"
    ui_cfg_path.write_text(
        (settings_path().parent / "schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "data_sources:\n  demo_dashboard:\n    type: demo\n\n",
            "data_sources:\n  unsafe_dashboard:\n    type: static\n    format: json\n    path: tests/fixtures/demo_static/dashboard_unsafe.json\n\n",
            1,
        )
        .replace("source: demo_dashboard", "source: unsafe_dashboard"),
        encoding="utf-8",
    )

    assert fixture_path.is_file()

    ui_config = load_beeui_config(ui_cfg_path)
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "<script>alert(7)</script>" not in response.text
    assert "&lt;script&gt;alert(7)&lt;/script&gt;" in response.text


def test_theme_and_layout_schema_are_rendered() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'data-bs-theme="dark"' in response.text
    assert "beeui-theme-primary-blue" in response.text
    assert "beeui-theme-base-gray" in response.text
    assert "beeui-density-default" in response.text
    assert "beeui-layout-vertical" in response.text
    assert "container-xl" in response.text


def test_dark_sidebar_renders_dark_theme_attribute() -> None:
    response = TestClient(create_beeui_app()).get("/")

    assert response.status_code == 200
    assert (
        'class="navbar navbar-vertical navbar-expand-lg beeui-sidebar '
        "beeui-sidebar-variant-dark "
        '"\n  data-bs-theme="dark"'
    ) in response.text


def test_page_blocks_use_tabler_grid_without_wrapper_card() -> None:
    response = TestClient(create_beeui_app()).get("/")

    assert response.status_code == 200
    page_blocks = response.text.split(
        '<section aria-label="Page blocks">',
        1,
    )[1].split("</section>", 1)[0]
    assert 'class="card p-3"' not in page_blocks
    assert 'class="row row-deck row-cards beeui-block-grid"' in page_blocks


def test_sidebar_renders_generic_navigation_icons() -> None:
    response = TestClient(create_beeui_app()).get("/")

    assert response.status_code == 200
    for icon in ("dashboard", "runs", "reports"):
        assert f'data-beeui-icon="{icon}"' in response.text
    assert response.text.count("data-beeui-icon=") == 3
    assert 'class="ti ti-dashboard icon icon-1"' in response.text
    assert "http://" not in response.text.lower()
    assert "https://" not in response.text.lower()


def test_light_theme_fixture_renders_from_schema() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    ui_config = replace(ui_config, theme=replace(ui_config.theme, mode="light"))
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'data-bs-theme="light"' in response.text
    assert "beeui-theme-mode-light" in response.text


def test_system_theme_fixture_renders_resolved_default_theme() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    ui_config = replace(ui_config, theme=replace(ui_config.theme, mode="system"))
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'data-bs-theme="light"' in response.text
    assert "beeui-theme-mode-light" in response.text
    assert "localStorage" in response.text


def test_login_uses_configured_theme_contract() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    ui_config = replace(ui_config, theme=replace(ui_config.theme, mode="dark"))
    client = TestClient(create_beeui_app(settings=settings, ui_config=ui_config))

    response = client.get("/auth/login")

    assert response.status_code == 200
    assert 'data-bs-theme="dark"' in response.text
    assert 'data-beeui-theme-config="dark"' in response.text
    assert "beeui-theme" in response.text


def test_theme_controls_use_beeui_catalog_for_russian_locale() -> None:
    client = TestClient(create_beeui_app())

    sidebar = client.get("/?lang=ru")
    login = client.get("/auth/login?lang=ru")

    for response in (sidebar, login):
        assert response.status_code == 200
        assert 'aria-label="Системная тема"' in response.text
        assert 'title="Системная"' in response.text
        assert 'aria-label="Светлая тема"' in response.text
        assert 'title="Светлая"' in response.text
        assert 'aria-label="Тёмная тема"' in response.text
        assert 'title="Тёмная"' in response.text
    assert "Тема" in sidebar.text


def test_navbar_disabled_fixture_does_not_render_top_navbar() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    navbar = replace(ui_config.layout.navbar, enabled=False)
    ui_config = replace(
        ui_config,
        layout=replace(ui_config.layout, navbar=navbar),
    )
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "beeui-navbar beeui-navbar-variant-default" not in response.text
    assert "beeui-sidebar beeui-sidebar-variant-dark" in response.text


def test_logo_text_from_schema_is_escaped(tmp_path: Path) -> None:
    settings = load_settings(settings_path())

    ui_cfg_path = tmp_path / "schema.yml"
    ui_cfg_path.write_text(
        (settings_path().parent / "schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  logo_text:\n    en: BeeUI\n    ru: BeeUI\n",
            '  logo_text:\n    en: "<script>alert(3)</script>"\n    ru: "<script>alert(3)</script>"\n',
            1,
        ),
        encoding="utf-8",
    )

    ui_config = load_beeui_config(ui_cfg_path)
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "<script>alert(3)</script>" not in response.text
    assert "&lt;script&gt;alert(3)&lt;/script&gt;" in response.text


def test_component_catalog_escapes_unsafe_sample_strings() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/components/interface")

    assert response.status_code == 200
    assert "<script>alert(6)</script>" not in response.text
    assert "&lt;script&gt;alert(6)&lt;/script&gt;" in response.text
    assert '<svg onload="alert(1)"></svg>' not in response.text
    assert "&lt;svg onload=&#34;alert(1)&#34;&gt;&lt;/svg&gt;" in response.text


def test_component_catalog_plugin_placeholders_are_inert() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/components/plugins")

    assert response.status_code == 200
    assert 'data-plugin="chart"' in response.text
    assert 'data-plugin="map"' in response.text
    assert 'data-plugin="datatable"' in response.text
    assert "cdn" not in response.text.lower()
    assert "http://" not in response.text.lower()
    assert "https://" not in response.text.lower()


def test_component_catalog_progress_uses_native_element_without_inline_style() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/components/layout")

    assert response.status_code == 200
    assert "<progress" in response.text
    assert 'style="' not in response.text


def test_component_catalog_url_tabs_use_query_active_state() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/components/interface?tab=overview")

    assert response.status_code == 200
    assert 'class="nav' in response.text
    assert "nav-tabs card-header-tabs" in response.text
    overview_active = re.search(
        r'href="[^"]*\?tab=overview"[^>]*class="[^"]*nav-link[^"]*active[^"]*"[^>]*aria-current="page"',
        response.text,
    )
    assert overview_active is not None, (
        "Overview tab must be active with aria-current when ?tab=overview"
    )
    details_not_active = re.search(
        r'href="[^"]*\?tab=details"[^>]*class="nav-link[^"]*"[^>]*aria-current="page"',
        response.text,
    )
    assert details_not_active is None, (
        "Details tab must NOT have aria-current when ?tab=overview"
    )


def test_component_catalog_url_tabs_invalid_tab_falls_back() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/components/interface?tab=nonexistent")

    assert response.status_code == 200
    details_active = re.search(
        r'href="[^"]*\?tab=details"[^>]*class="[^"]*nav-link[^"]*active[^"]*"[^>]*aria-current="page"',
        response.text,
    )
    assert details_active is not None, (
        "Details tab must be active when ?tab=nonexistent"
    )


def test_product_dashboard_disclosure_uses_accordion_primitive() -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result

    class AccordionTestAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard",),
                )
            )

        def get_dashboard(self):
            return ok_result(
                {
                    "latest_run": {"id": "run_1", "status": "ok"},
                    "summary": {"mode": "test"},
                }
            )

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

    app = create_beeui_app(adapter=AccordionTestAdapter())
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "<details" not in response.text
    assert 'class="accordion' in response.text
    assert 'class="accordion-button' in response.text
    assert 'class="accordion-button-toggle"' in response.text
    assert 'data-bs-toggle="collapse"' in response.text


def test_accordion_variant_from_config_affects_rendered_class(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.pages.config import load_beeui_config
    from beeui_module.web.app import create_beeui_app

    class AccordionVariantAdapter(ProductUiAdapterBase):
        def __init__(self):
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0.0",
                    capabilities=("dashboard",),
                )
            )

        def get_dashboard(self):
            return ok_result(
                {"latest_run": {"id": "run_1", "status": "ok"}, "summary": {}}
            )

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

    ui_config = load_beeui_config(schema_path)
    app = create_beeui_app(ui_config=ui_config, adapter=AccordionVariantAdapter())
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="accordion accordion-tabs"' in response.text


def test_page_tabs_render_in_html(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
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
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      variant: fill\n"
        "      active_param: tab\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /?tab=overview\n"
        "        - id: details\n"
        "          title: Details\n"
        "          href: /?tab=details\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "nav nav-tabs card-header-tabs nav-fill" in response.text
    assert 'href="/?tab=overview"' in response.text
    assert 'href="/?tab=details"' in response.text
    overview_active = re.search(
        r'href="/\?tab=overview"[^>]*class="[^"]*nav-link[^"]*active[^"]*"[^>]*aria-current="page"',
        response.text,
    )
    details_active = re.search(
        r'href="/\?tab=details"[^>]*class="[^"]*nav-link[^"]*active[^"]*"[^>]*aria-current="page"',
        response.text,
    )
    assert overview_active is not None
    assert details_active is None


def test_page_tabs_disabled_query_falls_back_to_first_enabled(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
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
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      variant: fill\n"
        "      active_param: tab\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /?tab=overview\n"
        "        - id: disabled_tab\n"
        "          title: Disabled\n"
        "          href: /?tab=disabled_tab\n"
        "          disabled: true\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?tab=disabled_tab")

    assert response.status_code == 200
    overview_active = re.search(
        r'href="/\?tab=overview"[^>]*class="[^"]*nav-link[^"]*active[^"]*"[^>]*aria-current="page"',
        response.text,
    )
    disabled_active = re.search(
        r">\s*Disabled\s*</a>",
        response.text,
    )
    disabled_span = re.search(
        r'<span class="nav-link disabled" role="tab" aria-disabled="true">\s*Disabled\s*</span>',
        response.text,
    )
    assert overview_active is not None
    assert disabled_active is None
    assert disabled_span is not None


def test_page_tabs_href_respects_route_prefix(tmp_path: Path) -> None:
    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
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
        "  - title: Custom\n"
        "    path: /rop\n"
        "    icon: file\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: custom_page\n"
        "    path: /rop\n"
        "    title: Custom Page\n"
        "    subtitle: Adapter-backed\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      active_param: tab\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /rop?tab=overview\n"
        "        - id: details\n"
        "          title: Details\n"
        "          href: /rop?tab=details\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    prefixed_settings = {
        **settings,
        "web": {**settings["web"], "route_prefix": "/ui"},
    }
    app = create_beeui_app(settings=prefixed_settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/ui/rop")

    assert response.status_code == 200
    assert 'href="/ui/rop?tab=overview"' in response.text
    assert 'href="/ui/rop?tab=details"' in response.text
    assert 'href="/rop?tab=overview"' not in response.text


def test_page_tabs_renders_attached_card(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
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
        "\n"
        "data_sources: {}\n"
        "blocks:\n"
        "  test_block:\n"
        "    type: text_card\n"
        "    title: Test Block\n"
        "    text: Block content here\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo subtitle\n"
        "    blocks:\n"
        "      - block: test_block\n"
        "        width: 6\n"
        "    tabs:\n"
        "      active_param: tab\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /?tab=overview\n"
        "        - id: details\n"
        "          title: Details\n"
        "          href: /?tab=details\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="card beeui-page-tabs-card"' in response.text
    assert "Demo subtitle" in response.text

    tabs_card_idx = response.text.index('class="card beeui-page-tabs-card"')
    title_idx = response.text.index("Demo subtitle")
    assert title_idx < tabs_card_idx, (
        "Page subtitle must appear before beeui-page-tabs-card"
    )

    page_blocks_section = response.text.index(
        '<section aria-label="Page blocks">', tabs_card_idx
    )
    card_body_idx = response.text.index('class="card-body"', tabs_card_idx)
    assert page_blocks_section > card_body_idx, (
        "Page blocks section must be inside card-body"
    )

    assert "Test Block" in response.text
    assert "Block content here" in response.text
    assert 'href="/?tab=overview"' in response.text
    assert 'href="/?tab=details"' in response.text
    card_segment = response.text[tabs_card_idx:]
    assert (
        card_segment.index('class="card-header"')
        < card_segment.index("nav nav-tabs card-header-tabs")
        < card_segment.index('class="card-body"')
        < card_segment.index('<section aria-label="Page blocks">')
    )


def test_page_tabs_no_standalone_tabs_card(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
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
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      active_param: tab\n"
        "      surface: separated\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /?tab=overview\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert (
        'class="beeui-page-tabs-card beeui-page-tabs-card-separated"' in response.text
    )
    assert (
        'class="card beeui-page-tabs-card beeui-page-tabs-card-separated"'
        not in response.text
    )

    tabs_card_start = response.text.index(
        'class="beeui-page-tabs-card beeui-page-tabs-card-separated"'
    )
    before_tabs_card = response.text[:tabs_card_start]
    assert "card-header-tabs" not in before_tabs_card, (
        "Must not contain standalone tabs card before beeui-page-tabs-card"
    )
    assert '<div class="card mb-3">' not in before_tabs_card
    page_blocks_start = response.text.index(
        'class="beeui-page-tabs-blocks" aria-label="Page blocks"'
    )
    assert '<div class="card">' in response.text[tabs_card_start:page_blocks_start]
    assert 'class="beeui-page-tabs-blocks" aria-label="Page blocks"' in response.text


def test_page_without_tabs_renders_blocks_normally(tmp_path: Path) -> None:
    from beeui_module.web.app import create_beeui_app

    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
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
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="card beeui-page-tabs-card"' not in response.text
    assert '<section aria-label="Page blocks">' in response.text
