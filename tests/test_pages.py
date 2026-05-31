from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from beeui_module.pages.config import load_beeui_config
from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
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
        "\n"
        "navigation:\n"
        '  - title: "<script>alert(1)</script>"\n'
        "    path: /\n"
        "    icon: dashboard\n"
        "\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        '    title: "<script>alert(1)</script>"\n'
        '    subtitle: "<script>alert(2)</script>"\n'
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
