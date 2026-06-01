from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.pages.config import load_beeui_config
from beeui_module.web.app import create_beeui_app


# Тест: чек, что страницы, сконфигурированные в YAML, рендерятся и доступны по своим путям
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


# Тест: чек, что для навигационного элемента, соответствующего текущему пути, добавляется класс is-active
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


# Тест: disabled navigation item рендерится безопасно без ссылки
def test_disabled_navigation_item_is_rendered_safely() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'aria-disabled="true"' in response.text
    assert "beeui-nav-disabled" in response.text


# Тест: чек, что запрос к несуществующей странице возвращает 404
def test_unknown_page_returns_404() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/missing")

    assert response.status_code == 404


# Тест: чек, что строки, предоставленные в конфиге, экранируются для предотвращения XSS
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
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        '    title: "<script>alert(1)</script>"\n'
        '    subtitle: "<script>alert(2)</script>"\n'
        "    blocks: []\n"
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
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in response.text


# Тест: empty state рендерится через component template
def test_empty_state_component_is_rendered() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "No blocks configured" in response.text
    assert "No blocks are configured for this page yet." in response.text


# Тест: theme/layout schema values прокидываются в HTML как safe classes and attributes
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


# Тест: чек, что при смене темы на light в конфиге, в HTML добавляются соответствующие атрибуты и классы для light темы
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


# Тест: theme.mode auto рендерится безопасно без client-side persistence/mutation
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


# Тест: чек, что при отключении навбара в конфиге, HTML не содержит классы для навбара и рендерит только сайдбар
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


# Тест: logo_text из schema экранируется в HTML
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
