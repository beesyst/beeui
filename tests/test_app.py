from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version
from beeui_module.web.app import create_beeui_app


# Тест: фабрика возвращает FastAPI-приложение
def test_create_beeui_app_returns_fastapi_app() -> None:
    app = create_beeui_app()

    assert isinstance(app, FastAPI)


# Тест: главная страница доступна и содержит безопасные заголовки
def test_get_index_returns_html() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Dashboard" in response.text
    assert "Demo operator dashboard" in response.text
    assert 'href="/runs"' in response.text
    assert response.headers["X-BeeUI-Read-Only"] == "true"
    assert response.headers["Cache-Control"] == "no-store"


# Тест: страница runs доступна и возвращает HTML
def test_get_runs_returns_html() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/runs")

    assert response.status_code == 200
    assert "Runs" in response.text
    assert "Placeholder page for future run overview" in response.text


# Тест: health endpoint возвращает ожидаемый JSON и read-only заголовки
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


# Тест: локальный CSS доступен через static route
def test_get_static_css_returns_file() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/static/css/beeui.css")

    assert response.status_code == 200
    assert "--bg:" in response.text
    assert response.headers["X-BeeUI-Read-Only"] == "true"


# Тест: HTML не содержит внешние URL и трекинг-скрипты
def test_html_does_not_include_external_assets_or_tracking() -> None:
    app = create_beeui_app()
    client = TestClient(app)

    response = client.get("/")
    html = response.text.lower()

    assert "http://" not in html
    assert "https://" not in html
    assert "posthog" not in html
    assert "scripts.tabler.io" not in html
    assert "preview/js/demo" not in html
    assert "preview/css/demo" not in html


# Тест: Jinja autoescape предотвращает вставку сырого script из title
def test_product_title_is_escaped_in_html() -> None:
    settings = load_settings(settings_path())
    settings["product"]["title"] = "<script>alert(1)</script>"

    app = create_beeui_app(settings=settings)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text


# Тест: missing обязательного web.port вызывает fail-fast ошибку
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


# Тест: invalid web.port вызывает fail-fast ошибку
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


# Тест: missing обязательного web.cache_static вызывает fail-fast ошибку
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


# Тест: invalid web.cache_static вызывает fail-fast ошибку
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


# Тест: missing security.assets_ext вызывает fail-fast ошибку
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


# Тест: invalid security.assets_ext вызывает fail-fast ошибку
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


# Тест: missing features.browser_artifact вызывает fail-fast ошибку
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
