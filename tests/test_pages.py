from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.pages.config import load_beeui_config
from beeui_module.web.app import create_beeui_app


# Страницы из schema.yml должны рендериться как HTML routes
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


# Тест: текущий route должен помечать соответствующий navigation item active-классом
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


# Тест: disabled navigation item рендерится без href и с aria-disabled
def test_disabled_navigation_item_is_rendered_safely() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'aria-disabled="true"' in response.text
    assert "beeui-nav-disabled" in response.text


# Тест: необъявленные страницы должны оставаться 404
def test_unknown_page_returns_404() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/missing")

    assert response.status_code == 404


# Тест: schema-provided строки должны экранироваться Jinja autoescape
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


# Тест: страница без placements показывает общий empty state component
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


# Тест: dashboard собирается из всех block types, объявленных в demo schema
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


# Тест: non-normal block states должны быть видимы в HTML без runtime resolver
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


# Тест: invalid selector syntax в резолвере должен возвращать envelope с ошибкой и предупреждением
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


# Тест: invalid selector syntax в резолвере должен возвращать envelope с ошибкой и предупреждением
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


# Тест: invalid selector syntax в резолвере должен возвращать envelope с ошибкой и предупреждением
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


# Тест: theme/layout schema values должны попадать только в валидированные classes
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


# Тест: dark sidebar получает локальный Bootstrap theme context
def test_dark_sidebar_renders_dark_theme_attribute() -> None:
    response = TestClient(create_beeui_app()).get("/")

    assert response.status_code == 200
    assert (
        'class="navbar navbar-vertical navbar-expand-lg beeui-sidebar '
        "beeui-sidebar-variant-dark "
        '"\n  data-bs-theme="dark"'
    ) in response.text


# Тест: page blocks используют canonical Tabler grid без wrapper card
def test_page_blocks_use_tabler_grid_without_wrapper_card() -> None:
    response = TestClient(create_beeui_app()).get("/")

    assert response.status_code == 200
    page_blocks = response.text.split(
        '<section aria-label="Page blocks">',
        1,
    )[1].split("</section>", 1)[0]
    assert 'class="card p-3"' not in page_blocks
    assert 'class="row row-deck row-cards beeui-block-grid"' in page_blocks


# Тест: navigation icon names рендерятся только через inline allowlist
def test_sidebar_renders_allowlisted_navigation_icons() -> None:
    response = TestClient(create_beeui_app()).get("/")

    assert response.status_code == 200
    for icon in ("dashboard", "runs", "reports"):
        assert f'data-beeui-icon="{icon}"' in response.text
    assert response.text.count("data-beeui-icon=") == 3
    assert "http://" not in response.text.lower()
    assert "https://" not in response.text.lower()


# Тест: light mode должен менять только theme attribute/classes
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


# Тест: auto theme не должен включать client-side persistence через localStorage
def test_auto_theme_fixture_renders_without_localstorage_mutation() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    ui_config = replace(ui_config, theme=replace(ui_config.theme, mode="auto"))
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'data-bs-theme="auto"' in response.text
    assert "beeui-theme-mode-auto" in response.text
    assert "localStorage" not in response.text


# Тест: navbar можно отключить schema-флагом без влияния на sidebar
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


# Тест: logo_text из schema остаётся plain text и экранируется
def test_logo_text_from_schema_is_escaped(tmp_path: Path) -> None:
    settings = load_settings(settings_path())

    ui_cfg_path = tmp_path / "schema.yml"
    ui_cfg_path.write_text(
        (settings_path().parent / "schema.yml")
        .read_text(encoding="utf-8")
        .replace(
            "  logo_text: BeeUI\n",
            '  logo_text: "<script>alert(3)</script>"\n',
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


# Тест: catalog section экранирует unsafe sample strings
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


# Тест: plugin placeholders остаются инертными и не тянут внешние assets
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


# Тест: catalog progress primitive не использует inline style
def test_component_catalog_progress_uses_native_element_without_inline_style() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/components/layout")

    assert response.status_code == 200
    assert "<progress" in response.text
    assert 'style="' not in response.text


# Тест: primitives catalog template не использует unsafe Jinja filter
def test_component_primitives_template_avoids_safe_filter() -> None:
    template_text = Path(
        "src/beeui_module/web/templates/components/primitives/catalog_primitives.html"
    ).read_text(encoding="utf-8")

    assert "|safe" not in template_text


# Тест: locale разрешается из config default
def test_locale_resolved_from_config() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200


# Тест: ?lang= override разрешается только если allowlist содержит
def test_locale_lang_query_updates_html_lang() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=ru")

    assert response.status_code == 200
    assert '<html lang="ru"' in response.text


# Тест: ?lang= override игнорируется если allowlist не содержит
def test_locale_invalid_lang_falls_back_to_default_html_lang() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/?lang=bad")

    assert response.status_code == 200
    assert '<html lang="en"' in response.text


# Тест: locale не падает без locale в config (fallback default)
def test_locale_missing_uses_default(tmp_path: Path) -> None:
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
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "blocks: {}\n"
        "data_sources: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
    )
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(ui_cfg_path)
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200


# Тест: URL-driven tabs в каталоге используют ?tab= для active
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


# Тест: невалидный ?tab= fallback к default
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


# Тест: fallback disclosure использует BeeUI accordion primitive, а не raw <details>
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


# Тест: accordion variant из config влияет на rendered class
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


# Тест: custom page, объявленная в schema с path, рендерится через adapter get_page
def _custom_page_schema(
    tmp_path: Path,
    custom_path: str,
    *,
    page_id: str = "custom_page",
    route_mode: str | None = None,
    page_blocks: str = "    blocks: []\n",
    extra_blocks: str = "blocks: {}\n",
) -> Path:
    route_config = (
        f"    route:\n      mode: {route_mode}\n" if route_mode is not None else ""
    )
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


# Генерация schema с кастомной страницей для тестов ниже
def _app_route_paths(app) -> set[str]:
    return {
        route.path
        for route in app.routes
        if isinstance(getattr(route, "path", None), str)
    }


# Тест: custom page, объявленная в schema с path, рендерится через adapter get_page
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


# Тест: если get_page возвращает ошибку, рендерится degraded/empty state для страницы
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


# Тест: системные BeeUI paths (/health) с matching page проходят config validation
def test_custom_page_route_health_is_not_registered(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class HealthPageAdapter(ProductUiAdapterBase):
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

    ui_cfg_path = _custom_page_schema(tmp_path, "/health")
    config = load_beeui_config(ui_cfg_path)
    assert any(p.path == "/health" for p in config.pages)

    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=HealthPageAdapter(),
    )
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("app") == "beeui"


# Тест: GET пользовательской страницы не должен мутировать исходный конфиг (например, через resolver с side effect)
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


# Тест: page tabs рендерятся с разметкой nav nav-tabs card-header-tabs
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


# Тест: page tabs href должен учитывать route_prefix из settings
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


# Тест: если get_page возвращает malformed payload, рендерится degraded/empty state для страницы
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


# Тест: если get_page возвращает payload с секретными данными, они редактируются перед рендером
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
                            "type": "raw_json_panel",
                            "title": "Debug",
                            "data": {"api_key": "secret-value"},
                        }
                    ]
                }
            )

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=RedactedPageAdapter(),
    )
    client = TestClient(app)

    response = client.get("/rop")

    assert response.status_code == 200
    assert "secret-value" not in response.text


# Тест: page tabs рендерятся внутри карточки и после subtitle страницы
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


# Тест: page tabs nav находится внутри header той же attached card
def test_page_tabs_nav_is_inside_attached_card_header(tmp_path: Path) -> None:
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
        "          href: /?tab=overview\n",
        encoding="utf-8",
    )

    ui_config = load_beeui_config(schema_path)
    settings = load_settings(settings_path())
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200

    card_start = response.text.index('class="card beeui-page-tabs-card"')
    card_segment = response.text[card_start:]

    header_idx = card_segment.index('class="card-header"')
    nav_idx = card_segment.index("nav nav-tabs card-header-tabs")
    body_idx = card_segment.index('class="card-body"')
    blocks_idx = card_segment.index('<section aria-label="Page blocks">')

    assert header_idx < nav_idx < body_idx < blocks_idx


# Тест: page tabs рендерятся без дублирующей standalone карточки с card-header-tabs
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
    assert 'class="card beeui-page-tabs-card"' in response.text

    tabs_card_start = response.text.index('class="card beeui-page-tabs-card"')
    before_tabs_card = response.text[:tabs_card_start]
    assert "card-header-tabs" not in before_tabs_card, (
        "Must not contain standalone tabs card before beeui-page-tabs-card"
    )
    assert '<div class="card mb-3">' not in before_tabs_card


# Тест: страница без tabs рендерит blocks без tabs-card и nav-tabs
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


# Тест: /rop регистрируется как adapter-backed custom page route
def test_custom_route_rop_registers_with_adapter(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

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
                {"layout": [{"type": "metric_card", "title": "ROP", "value": "42"}]}
            )

    ui_cfg_path = _custom_page_schema(tmp_path, "/rop")
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=RopPageAdapter(),
    )
    client = TestClient(app)

    response = client.get("/rop")
    assert response.status_code == 200
    assert "ROP" in response.text
    assert "42" in response.text


# Тест: /venues/mrkt с route.mode=metadata не регистрирует concrete page route
def test_metadata_route_venues_mrkt_skipped(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

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

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/venues/mrkt",
        route_mode="metadata",
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=VenuePageAdapter(),
    )
    route_paths = _app_route_paths(app)
    assert "/venues/mrkt" not in route_paths
    assert "/venues/{venue_id}" in route_paths

    client = TestClient(app)

    response = client.get("/venues/mrkt")
    assert response.status_code == 503
    assert "Custom Page" not in response.text


# Тест: /venues/binance с route.mode=metadata не регистрирует concrete page route
def test_metadata_route_venues_binance_skipped(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

    class VenueBinanceAdapter(ProductUiAdapterBase):
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
        "/venues/binance",
        route_mode="metadata",
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=VenueBinanceAdapter(),
    )
    route_paths = _app_route_paths(app)
    assert "/venues/binance" not in route_paths
    assert "/venues/{venue_id}" in route_paths

    client = TestClient(app)

    response = client.get("/venues/binance")
    assert response.status_code == 503
    assert "Custom Page" not in response.text


# Тест: /runs/run_001 с route.mode=metadata не регистрирует concrete page route
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


# Тест: arbitrary nested route.mode=adapter регистрируется и вызывает adapter.get_page
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


# Тест: arbitrary nested route.mode=configured регистрируется как schema page
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
            "    value: \"99\"\n"
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


def test_modes_live_adapter_route_registers(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

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

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/modes/live",
        route_mode="adapter",
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=ModesPageAdapter(),
    )

    route_paths = _app_route_paths(app)
    assert "/modes/live" in route_paths

    response = TestClient(app).get("/modes/live")
    assert response.status_code == 200
    assert "Mode" in response.text


def test_modes_live_metadata_route_skipped(tmp_path: Path) -> None:
    from beeui_module.adapters.base import ProductUiAdapterBase
    from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
    from beeui_module.web.app import create_beeui_app

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

    ui_cfg_path = _custom_page_schema(
        tmp_path,
        "/modes/live",
        route_mode="metadata",
    )
    app = create_beeui_app(
        config_path=str(ui_cfg_path),
        adapter=ModesPageAdapter(),
    )

    route_paths = _app_route_paths(app)
    assert "/modes/live" not in route_paths


# Тест: system reserved paths не регистрируются как custom pages
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
