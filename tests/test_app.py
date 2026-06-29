from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version
from beeui_module.pages.config import load_beeui_config
from beeui_module.web.app import create_beeui_app


def test_create_beeui_app_returns_fastapi_app() -> None:
    app = create_beeui_app()

    assert isinstance(app, FastAPI)


def test_get_index_returns_html() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Dashboard" in response.text
    assert "Demo operator dashboard" in response.text
    assert "Workspace" in response.text
    assert 'href="/runs"' in response.text
    assert response.headers["X-BeeUI-Read-Only"] == "true"
    assert response.headers["Cache-Control"] == "no-store"


def test_get_runs_returns_html() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/runs")

    assert response.status_code == 200
    assert "Runs" in response.text
    assert "Placeholder page for future run overview" in response.text


def test_component_catalog_routes_render() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    routes = [
        "/components",
        "/components/interface",
        "/components/forms",
        "/components/layout",
        "/components/extra",
        "/components/plugins",
    ]

    for route in routes:
        response = client.get(route)
        assert response.status_code == 200
        assert response.headers["X-BeeUI-Read-Only"] == "true"
        assert response.headers["Cache-Control"] == "no-store"


def test_component_catalog_routes_follow_route_prefix() -> None:
    settings = load_settings(settings_path())
    settings["web"]["route_prefix"] = "/bee"

    app = create_beeui_app(settings=settings)
    client = TestClient(app)

    prefixed = client.get("/bee/components")
    plain = client.get("/components")

    assert prefixed.status_code == 200
    assert plain.status_code == 404


def test_component_catalog_internal_links_follow_route_prefix() -> None:
    settings = load_settings(settings_path())
    settings["web"]["route_prefix"] = "/bee"

    app = create_beeui_app(settings=settings)
    client = TestClient(app)

    response = client.get("/bee/components/layout")

    assert response.status_code == 200
    assert 'href="/bee/"' in response.text
    assert 'href="/bee/components"' in response.text
    assert 'href="/components"' not in response.text


def test_get_health_returns_expected_payload() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "beeui",
        "version": get_version(),
        "read_only": True,
    }
    assert response.headers["X-BeeUI-Read-Only"] == "true"
    assert response.headers["Cache-Control"] == "no-store"


def test_get_static_css_returns_file() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/static/css/beeui.css")

    assert response.status_code == 200
    assert "--beeui-sidebar-bg:" in response.text
    assert response.headers["X-BeeUI-Read-Only"] == "true"


def test_get_local_tabler_vendor_asset_returns_file() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/static/vendor/tabler/css/tabler.min.css")

    assert response.status_code == 200
    assert "--tblr-body-bg:" in response.text
    assert "--tblr-primary-rgb:" in response.text
    assert "Tabler v1.4.0" in response.text
    assert response.headers["X-BeeUI-Read-Only"] == "true"


def test_local_tabler_css_is_not_placeholder() -> None:
    css_path = Path("src/beeui_module/web/static/vendor/tabler/css/tabler.min.css")
    css = css_path.read_text(encoding="utf-8")

    assert css_path.stat().st_size > 100_000
    for marker in (
        ".page-wrapper",
        ".page-body",
        ".navbar-vertical",
        ".card",
        ".card-header",
        ".table-vcenter",
        ".badge",
        "--tblr-",
    ):
        assert marker in css

    lowered = css.lower()
    for forbidden in (
        "cdn.jsdelivr",
        "preview.tabler.io",
        "posthog",
        "scripts.tabler.io",
        "sourcemappingurl",
    ):
        assert forbidden not in lowered


def test_beeui_css_does_not_override_core_grid() -> None:
    css = Path("src/beeui_module/web/static/css/beeui.css").read_text(encoding="utf-8")

    for selector in (
        "\n.row {",
        "\n.col-lg-6 {",
        "\n.container-xl {",
        "\n.card {",
        "\n.table {",
        "\n.badge {",
        "\n.btn {",
    ):
        assert selector not in css


def test_beeui_theme_base_surface_override_is_theme_scoped() -> None:
    css = Path("src/beeui_module/web/static/css/beeui.css").read_text(encoding="utf-8")

    light_rule = css.index('[data-bs-theme="light"] .beeui-theme-base-gray')
    light_value = css.index("--beeui-surface: #ffffff;", light_rule)
    dark_rule = css.index('[data-bs-theme="dark"] .beeui-theme-base-gray')
    dark_value = css.index(
        "--beeui-surface: var(--tblr-bg-surface);",
        dark_rule,
    )

    assert light_rule < light_value < dark_rule < dark_value
    assert "\n.beeui-theme-base-gray," not in css


def test_beeui_footer_override_is_transparent() -> None:
    css = Path("src/beeui_module/web/static/css/beeui.css").read_text(encoding="utf-8")
    footer_rule = css.split(".beeui-footer {", 1)[1].split("}", 1)[0]

    assert "background: transparent;" in footer_rule
    assert "border-top: 0;" in footer_rule
    assert "#fff" not in footer_rule.lower()
    assert "white" not in footer_rule.lower()


def test_get_local_tabler_vendor_js_asset_returns_file() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/static/vendor/tabler/js/tabler.min.js")

    assert response.status_code == 200
    assert "Tabler v1.4.0" in response.text
    assert "Bootstrap v5.3.7" in response.text
    assert "sourceMappingURL" not in response.text
    assert response.headers["X-BeeUI-Read-Only"] == "true"


def test_html_does_not_include_external_assets_or_tracking() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/")
    html = response.text.lower()

    assert "http://" not in html
    assert "https://" not in html
    assert "posthog" not in html
    assert "scripts.tabler.io" not in html
    assert "docs.tabler.io" not in html
    assert "preview.tabler.io" not in html
    assert "preview/js/demo" not in html
    assert "preview/css/demo" not in html
    assert "@import url(http" not in html


def test_default_dark_shell_has_no_navbar_and_transparent_footer() -> None:
    response = TestClient(create_beeui_app()).get("/")

    assert response.status_code == 200
    assert "beeui-navbar" not in response.text
    assert (
        'class="footer footer-transparent d-print-none beeui-footer"' in response.text
    )


def test_html_uses_real_local_tabler_assets() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    tabler_css = "/static/vendor/tabler/css/tabler.min.css"
    tabler_js = "/static/vendor/tabler/js/tabler.min.js"
    beeui_css = "/static/css/beeui.css"
    beeui_js = "/static/js/beeui.js"
    assert tabler_css in response.text
    assert tabler_js in response.text
    assert beeui_css in response.text
    assert beeui_js in response.text
    assert response.text.index(tabler_css) < response.text.index(beeui_css)
    assert response.text.index(tabler_js) < response.text.index(beeui_js)
    assert "http://" not in response.text
    assert "https://" not in response.text
    assert 'data-bs-theme="dark"' in response.text
    assert "beeui-theme-primary-blue" in response.text
    assert "beeui-theme-base-gray" in response.text


def test_product_title_is_escaped_in_html() -> None:
    settings = load_settings(settings_path())
    settings["product"]["title"] = "<script>alert(1)</script>"
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    ui_config = replace(
        ui_config,
        layout=replace(
            ui_config.layout,
            navbar=replace(ui_config.layout.navbar, enabled=True),
        ),
    )

    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text


def test_load_settings_fails_on_missing_web_port(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  route_prefix: ''\n"
        "  cache_static: 1\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "Missing required key: web.port"
    else:
        raise AssertionError("load_settings must fail fast when web.port is missing")


def test_load_settings_fails_on_invalid_web_port(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: bad\n"
        "  route_prefix: ''\n"
        "  cache_static: 1\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "web.port must be an integer in range 1..65535"
    else:
        raise AssertionError("load_settings must fail fast on invalid web.port")


def test_load_settings_fails_on_missing_web_cache_static(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "Missing required key: web.cache_static"
    else:
        raise AssertionError(
            "load_settings must fail fast when web.cache_static is missing"
        )


def test_load_settings_fails_on_invalid_web_cache_static(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "  cache_static: bad\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "web.cache_static must be an integer >= 0"
    else:
        raise AssertionError("load_settings must fail fast on invalid web.cache_static")


def test_load_settings_fails_on_missing_security_assets_ext(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "  cache_static: 1\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "Missing required key: security.assets_ext"
    else:
        raise AssertionError(
            "load_settings must fail fast when security.assets_ext is missing"
        )


def test_load_settings_fails_on_invalid_security_assets_ext(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "  cache_static: 1\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: bad\n"
        "features:\n"
        "  browser_artifact: false\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "security.assets_ext must be a boolean"
    else:
        raise AssertionError(
            "load_settings must fail fast on invalid security.assets_ext"
        )


def test_load_settings_fails_on_missing_features_browser_artifact(tmp_path) -> None:
    config_path = tmp_path / "settings.yml"
    config_path.write_text(
        "app:\n"
        "  name: beeui\n"
        "web:\n"
        "  host: 127.0.0.1\n"
        "  port: 8780\n"
        "  route_prefix: ''\n"
        "  cache_static: 1\n"
        "logging:\n"
        "  clear_logs: true\n"
        "  utc: true\n"
        "  level: INFO\n"
        "  file: logs/app.log\n"
        "security:\n"
        "  html_autoescape: true\n"
        "  assets_ext: false\n"
        "features:\n"
        "  config_preview: false\n"
        "  config_apply: false\n"
        "  operator_actions: false\n"
        "  api: false\n"
        "storage:\n"
        "  enabled: true\n"
        "  root: storage\n"
        "product:\n"
        "  id: demo\n"
        "  title: BeeUI Demo\n",
        encoding="utf-8",
    )

    try:
        load_settings(config_path)
    except ValueError as exc:
        assert str(exc) == "Missing required key: features.browser_artifact"
    else:
        raise AssertionError(
            "load_settings must fail fast when features.browser_artifact is missing"
        )


def test_page_with_tabs_renders_tabs_card() -> None:
    from dataclasses import replace

    from beeui_module.pages.models import PageTabsConfig, PageTabsItem

    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    ui_config = replace(
        ui_config,
        pages=[
            replace(
                ui_config.pages[0],
                tabs=PageTabsConfig(
                    items=(PageTabsItem(tab_id="tab1", title="Tab 1", href="/"),),
                ),
            ),
            ui_config.pages[1],
        ],
    )
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert 'class="card beeui-page-tabs-card"' in response.text
    assert "Tab 1" in response.text


def test_page_without_tabs_renders_normal_blocks() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/runs")

    assert response.status_code == 200
    assert "beeui-page-tabs-card" not in response.text
    assert "No blocks configured" in response.text


def test_page_body_container_wrapper_consistent() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    for path in ("/", "/runs"):
        response = client.get(path)
        assert response.status_code == 200
        assert 'class="page-body"' in response.text
        body_idx = response.text.index('class="page-body"')
        container_idx = response.text.index("container-xl")
        assert container_idx > body_idx, (
            f"Path {path}: container-xl must be inside page-body"
        )


def test_configured_page_uses_page_body() -> None:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    app = create_beeui_app(settings=settings, ui_config=ui_config)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    body_idx = response.text.index('class="page-body"')
    container_idx = response.text.index("container-xl", body_idx)
    assert container_idx > body_idx
