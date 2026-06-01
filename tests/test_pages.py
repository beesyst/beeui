from __future__ import annotations

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
            "title: Runtime\n    status: ok",
            "title: Runtime\n    state: degraded\n    status: ok",
            1,
        )
        .replace(
            "title: Demo mode\n    message:",
            "title: Demo mode\n    state: error\n    message:",
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
