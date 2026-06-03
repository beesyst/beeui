from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient

from beeui_module.adapters.base import ProductUiAdapterBase
from beeui_module.adapters.envelopes import AdapterMetadata, ok_result
from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version
from beeui_module.pages.config import load_beeui_config
from beeui_module.pages.models import BeeUiConfig
from beeui_module.web.app import create_beeui_app, mount_beeui


# Фейк: минимальный валидный адаптер для тестирования инъекции API в embedded режиме
class FakeEmbeddedAdapter(ProductUiAdapterBase):
    def __init__(self) -> None:
        super().__init__(
            AdapterMetadata(
                product_id="product_test",
                title="Test Product",
                version="9.9.9",
                capabilities=("dashboard",),
                supported_pages=("/",),
            )
        )

    def get_dashboard(self) -> Any:
        return ok_result({"status": "embedded_ok"})

    def list_runs(self) -> Any:
        return ok_result([])

    def get_run(self, run_id: str) -> Any:
        from beeui_module.adapters.envelopes import error_result_from_exception
        from beeui_module.adapters.errors import NotFoundError

        return error_result_from_exception(NotFoundError("no runs yet"))

    def list_artifacts(self, run_id: str) -> Any:
        return ok_result([])

    def read_artifact(self, run_id: str, artifact_id: str) -> Any:
        from beeui_module.adapters.envelopes import error_result_from_exception
        from beeui_module.adapters.errors import NotFoundError

        return error_result_from_exception(NotFoundError("no artifact"))

    def get_config_read_model(self) -> Any:
        return ok_result({"mode": "embedded", "read_only": True})


class MissingMetadataAdapter:
    pass


class WrongMetadataTypeAdapter:
    metadata = "not an AdapterMetadata instance"


# Адаптер с метаданными, но без обязательных методов
class MissingMethodAdapter:
    def __init__(self) -> None:
        self.metadata = AdapterMetadata(
            product_id="broken",
            title="Broken",
            version="0.0.1",
        )


# Хелпер: запись словаря в YAML файл для тестов
def _write_beeui_yml(tmp_path: Path, content: dict[str, Any]) -> Path:
    path = tmp_path / "beeui.yml"
    path.write_text(yaml.safe_dump(content), encoding="utf-8")
    return path


# Хелпер: валидация адаптера при передаче в create_beeui_app - проверка наличия metadata и обязательных методов
def _route_paths(app: FastAPI) -> set[str]:
    paths: set[str] = set()
    for route in app.routes:
        route_path = getattr(route, "path", None)
        if isinstance(route_path, str):
            paths.add(route_path)
    return paths


# Валидация адаптера при передаче в create_beeui_app
def _minimal_beeui_config() -> dict[str, Any]:
    return {
        "app": {
            "title": "Embedded Test",
            "product": "test",
            "logo_text": "TestUI",
            "theme": {
                "mode": "dark",
                "primary": "blue",
                "base": "gray",
                "font": "sans-serif",
                "radius": 1,
                "density": "default",
            },
            "layout": {
                "type": "vertical",
                "container": "xl",
                "sidebar": {"variant": "dark", "collapsed": False},
                "navbar": {"enabled": True, "variant": "default", "sticky": False},
            },
        },
        "navigation": [
            {
                "title": "Main",
                "children": [
                    {"title": "Dashboard", "path": "/", "icon": "dashboard"},
                ],
            },
        ],
        "data_sources": {},
        "blocks": {},
        "pages": [
            {
                "id": "dashboard",
                "path": "/",
                "title": "Dashboard",
                "subtitle": "Embedded test",
                "blocks": [],
            },
        ],
    }


# Тесты: создание приложения в embedded режиме и его базовая функциональность
class TestDefaultCreateBeeuiApp:
    def test_returns_fastapi_app(self) -> None:
        app = create_beeui_app()
        assert isinstance(app, FastAPI)

    def test_index_renders(self) -> None:
        app = create_beeui_app()
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Dashboard" in resp.text

    def test_health_returns_expected_payload(self) -> None:
        app = create_beeui_app()
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {
            "status": "ok",
            "app": "beeui",
            "version": get_version(),
            "read_only": True,
        }

    def test_static_css_served(self) -> None:
        app = create_beeui_app()
        client = TestClient(app)
        resp = client.get("/static/css/beeui.css")
        assert resp.status_code == 200

    def test_read_only_header(self) -> None:
        app = create_beeui_app()
        client = TestClient(app)
        resp = client.get("/")
        assert resp.headers["X-BeeUI-Read-Only"] == "true"

    def test_no_api_routes(self) -> None:
        app = create_beeui_app()
        routes = _route_paths(app)
        api_routes = {route for route in routes if route.startswith("/api")}
        assert not api_routes, f"Unexpected /api/* routes: {api_routes}"


# Тесты: загрузка конфигурации из config_path и приоритет explicit ui_config над config_path
class TestCreateBeeuiAppWithConfigPath:
    def test_config_path_loads_routes(self, tmp_path: Path) -> None:
        config = _minimal_beeui_config()
        config_path = _write_beeui_yml(tmp_path, config)

        app = create_beeui_app(config_path=config_path)
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Embedded Test" in resp.text

    def test_config_path_fails_on_missing_path(self) -> None:
        missing = Path("/nonexistent/beeui.yml")
        try:
            create_beeui_app(config_path=missing)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("Expected FileNotFoundError for missing config_path")

    def test_config_path_fails_on_invalid_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "beeui.yml"
        path.write_text("invalid: [yaml: broken", encoding="utf-8")
        try:
            create_beeui_app(config_path=path)
        except Exception:
            pass
        else:
            raise AssertionError("Expected error for invalid YAML config_path")

    def test_explicit_ui_config_takes_precedence(self, tmp_path: Path) -> None:
        config_path_config = _minimal_beeui_config()
        config_path_config["app"]["title"] = "From Config Path"
        cp = _write_beeui_yml(tmp_path, config_path_config)

        explicit_config = load_beeui_config(cp)
        explicit_config = BeeUiConfig(
            app_title="Explicit Config",
            product=explicit_config.product,
            logo_text=explicit_config.logo_text,
            theme=explicit_config.theme,
            layout=explicit_config.layout,
            navigation=explicit_config.navigation,
            data_sources=explicit_config.data_sources,
            blocks=explicit_config.blocks,
            pages=explicit_config.pages,
        )

        app = create_beeui_app(ui_config=explicit_config, config_path=cp)
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Explicit Config" in resp.text


# Тесты: инъекция product_id и product_title в app.state и приоритет этих параметров над настройками из config_path
class TestProductMetadataInjection:
    def test_product_id_and_title_stored(self) -> None:
        app = create_beeui_app(
            product_id="beecap",
            product_title="BeeCap",
        )
        assert app.state.beeui_product["id"] == "beecap"
        assert app.state.beeui_product["title"] == "BeeCap"

    def test_product_metadata_overrides_settings(self) -> None:
        settings = load_settings(settings_path())
        assert settings["product"]["id"] == "demo"
        assert settings["product"]["title"] == "BeeUI Demo"

        app = create_beeui_app(
            settings=settings,
            product_id="beecap",
            product_title="BeeCap",
        )
        assert app.state.beeui_product["id"] == "beecap"
        assert app.state.beeui_product["title"] == "BeeCap"

    def test_product_metadata_does_not_mutate_settings(self) -> None:
        settings = load_settings(settings_path())
        original_id = settings["product"]["id"]
        original_title = settings["product"]["title"]

        create_beeui_app(
            settings=settings,
            product_id="beecap",
            product_title="BeeCap",
        )
        assert settings["product"]["id"] == original_id
        assert settings["product"]["title"] == original_title

    def test_default_product_metadata_when_not_provided(self) -> None:
        app = create_beeui_app()
        assert app.state.beeui_product["id"] == "demo"
        assert app.state.beeui_product["title"] == "BeeUI Demo"


# Тесты: инъекция адаптера в app.state и валидация адаптера при передаче в create_beeui_app
class TestAdapterInjection:
    def test_adapter_stored_in_app_state(self) -> None:
        adapter = FakeEmbeddedAdapter()
        app = create_beeui_app(adapter=adapter)
        assert app.state.beeui_adapter is adapter

    def test_adapter_product_metadata_in_state(self) -> None:
        adapter = FakeEmbeddedAdapter()
        app = create_beeui_app(
            product_id="beecap",
            product_title="BeeCap",
            adapter=adapter,
        )
        assert app.state.beeui_product["id"] == "beecap"
        assert app.state.beeui_product["product_id"] == "product_test"
        assert app.state.beeui_product["adapter_version"] == "9.9.9"
        assert "dashboard" in app.state.beeui_product["capabilities"]

    def test_invalid_adapter_missing_metadata_rejected(self) -> None:
        try:
            create_beeui_app(adapter=cast(Any, MissingMetadataAdapter()))
        except ValueError as exc:
            assert "metadata" in str(exc).lower()
        else:
            raise AssertionError("Expected ValueError for adapter without metadata")

    def test_invalid_adapter_wrong_metadata_type_rejected(self) -> None:
        try:
            create_beeui_app(adapter=cast(Any, WrongMetadataTypeAdapter()))
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for wrong metadata type")

    def test_invalid_adapter_missing_method_rejected(self) -> None:
        try:
            create_beeui_app(adapter=cast(Any, MissingMethodAdapter()))
        except ValueError as exc:
            assert "get_dashboard" in str(exc)
        else:
            raise AssertionError(
                "Expected ValueError for adapter missing required method"
            )


# Тесты: использование route_prefix в настройках и его влияние на маршруты и статические файлы
class TestRoutePrefixWithEmbedded:
    def test_route_prefix_works_with_product_metadata(self) -> None:
        settings = load_settings(settings_path())
        settings["web"]["route_prefix"] = "/bee"

        app = create_beeui_app(
            settings=settings,
            product_id="beecap",
            product_title="BeeCap",
        )
        client = TestClient(app)

        resp = client.get("/bee/")
        assert resp.status_code == 200
        assert "BeeCap" in resp.text

    def test_static_assets_under_route_prefix(self) -> None:
        settings = load_settings(settings_path())
        settings["web"]["route_prefix"] = "/bee"

        app = create_beeui_app(settings=settings)
        client = TestClient(app)

        resp = client.get("/bee/static/css/beeui.css")
        assert resp.status_code == 200

    def test_health_under_route_prefix(self) -> None:
        settings = load_settings(settings_path())
        settings["web"]["route_prefix"] = "/bee"

        app = create_beeui_app(settings=settings)
        client = TestClient(app)

        resp = client.get("/bee/health")
        assert resp.status_code == 200


# Тесты: монтирование BeeUI в существующее FastAPI приложение и базовая функциональность
class TestMountBeeui:
    def test_mount_exposes_health(self) -> None:
        parent = FastAPI()
        mount_beeui(parent, path="/ui")

        client = TestClient(parent)
        resp = client.get("/ui/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_mount_exposes_index(self) -> None:
        parent = FastAPI()
        mount_beeui(parent, path="/ui")

        client = TestClient(parent)
        resp = client.get("/ui/")
        assert resp.status_code == 200

    def test_mount_exposes_static(self) -> None:
        parent = FastAPI()
        mount_beeui(parent, path="/ui")

        client = TestClient(parent)
        resp = client.get("/ui/static/css/beeui.css")
        assert resp.status_code == 200

    def test_mount_with_product_metadata(self) -> None:
        parent = FastAPI()
        adapter = FakeEmbeddedAdapter()
        mount_beeui(
            parent,
            path="/beecap",
            product_id="beecap",
            product_title="BeeCap",
            adapter=adapter,
        )

        client = TestClient(parent)
        resp = client.get("/beecap/health")
        assert resp.status_code == 200

    def test_mount_with_config_path(self, tmp_path: Path) -> None:
        config = _minimal_beeui_config()
        config_path = _write_beeui_yml(tmp_path, config)

        parent = FastAPI()
        mount_beeui(parent, path="/custom", config_path=config_path)

        client = TestClient(parent)
        resp = client.get("/custom/")
        assert resp.status_code == 200
        assert "Embedded Test" in resp.text


# Тесты: валидация пути при монтировании и защита от небезопасных или некорректных путей
class TestMountPathValidation:
    def test_rejects_empty_path(self) -> None:
        parent = FastAPI()
        try:
            mount_beeui(parent, path="")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for empty path")

    def test_rejects_root_path(self) -> None:
        parent = FastAPI()
        try:
            mount_beeui(parent, path="/")
        except ValueError as exc:
            assert "use create_beeui_app directly" in str(exc)
        else:
            raise AssertionError("Expected ValueError for root path")

    def test_rejects_path_without_leading_slash(self) -> None:
        parent = FastAPI()
        try:
            mount_beeui(parent, path="ui")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for path without leading /")

    def test_rejects_path_with_dots(self) -> None:
        parent = FastAPI()
        try:
            mount_beeui(parent, path="/../ui")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for path with ..")

    def test_rejects_path_with_double_slash(self) -> None:
        parent = FastAPI()
        try:
            mount_beeui(parent, path="//ui")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for path with //")

    def test_rejects_path_with_query_chars(self) -> None:
        parent = FastAPI()
        try:
            mount_beeui(parent, path="/ui?foo=bar")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for path with query chars")

    def test_rejects_path_with_trailing_slash(self) -> None:
        parent = FastAPI()
        try:
            mount_beeui(parent, path="/ui/")
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError for trailing slash")


# Тесты: обнаружение конфликтов маршрутов при монтировании в существующее приложение
class TestRouteCollision:
    def test_conflicting_route_detected(self) -> None:
        parent = FastAPI()

        @parent.get("/ui/health")
        async def existing_route():
            return {"status": "existing"}

        try:
            mount_beeui(parent, path="/ui")
        except ValueError as exc:
            assert "conflicts" in str(exc).lower()
        else:
            raise AssertionError("Expected ValueError for conflicting route")


# Тесты: отсутствие /api/* маршрутов в embedded режиме, так как API не должно быть доступно напрямую
class TestNoApiRoutes:
    def test_no_api_routes_after_embedded_creation(self) -> None:
        adapter = FakeEmbeddedAdapter()
        app = create_beeui_app(
            product_id="beecap",
            product_title="BeeCap",
            adapter=adapter,
        )
        routes = _route_paths(app)
        api_routes = {route for route in routes if route.startswith("/api")}
        assert not api_routes, f"Unexpected /api/* routes: {api_routes}"

    def test_no_api_routes_after_mount(self) -> None:
        parent = FastAPI()
        mount_beeui(parent, path="/ui")
        routes = _route_paths(parent)
        api_routes = {route for route in routes if route.startswith("/api")}
        assert not api_routes, f"Unexpected /api/* routes: {api_routes}"
