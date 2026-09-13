from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.pages.config import load_beeui_config
from beeui_module.web.app import create_beeui_app


def _visibility_denied(denied: set[str]):
    def resolver(request, path):
        return path not in denied

    return resolver


def _visibility_request(
    resolver=None,
    *,
    path: str = "/",
) -> Request:
    from fastapi import FastAPI

    app = FastAPI()
    if resolver is not None:
        app.state.beeui_navigation_visibility = resolver

    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "headers": [],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "root_path": "",
            "app": app,
        }
    )


def _nav_item(
    title: str,
    path: str | None = None,
    *,
    children: list | None = None,
):
    from beeui_module.pages.models import BeeUiNavigationItem

    return BeeUiNavigationItem(title=title, path=path, children=children or [])


def _visibility_schema(tmp_path: Path) -> Path:
    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
        "  locale:\n"
        "    default: en\n"
        "    available:\n"
        "      - en\n"
        "      - ru\n"
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
        "  - title: Runs\n"
        "    path: /runs\n"
        "    icon: runs\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
        "  - id: runs\n"
        "    path: /runs\n"
        "    title: Runs\n"
        "    subtitle: Runs page\n"
        "    blocks: []\n",
        encoding="utf-8",
    )
    return schema_path


def test_build_navigation_without_resolver_keeps_all_items() -> None:
    from beeui_module.pages.router import build_navigation

    navigation = [
        _nav_item("Dashboard", "/"),
        _nav_item("Workspace", children=[_nav_item("Runs", "/runs")]),
    ]
    result = build_navigation(
        route_prefix="",
        navigation=navigation,
        active_path="/",
    )
    assert len(result) == 2
    assert result[0]["path"] == "/"
    assert result[1]["is_group"] is True
    assert [child["path"] for child in result[1]["children"]] == ["/runs"]


def test_build_navigation_resolver_without_request_fails_closed() -> None:
    from beeui_module.pages.router import build_navigation

    calls = 0

    def resolver(request, path):
        nonlocal calls
        calls += 1
        return True

    result = build_navigation(
        route_prefix="",
        navigation=[_nav_item("Runs", "/runs")],
        active_path="/",
        visibility_resolver=resolver,
    )

    assert result == []
    assert calls == 0


def test_build_navigation_resolver_hides_leaf_keeps_siblings() -> None:
    from beeui_module.pages.router import build_navigation

    navigation = [
        _nav_item("Dashboard", "/"),
        _nav_item("Runs", "/runs"),
        _nav_item("Reports", "/reports"),
    ]
    result = build_navigation(
        route_prefix="",
        navigation=navigation,
        active_path="/",
        request=_visibility_request(),
        visibility_resolver=_visibility_denied({"/runs"}),
    )
    assert [item["path"] for item in result] == ["/", "/reports"]


def test_build_navigation_group_without_visible_children_omitted() -> None:
    from beeui_module.pages.router import build_navigation

    navigation = [
        _nav_item(
            "Workspace",
            children=[_nav_item("Dashboard", "/"), _nav_item("Runs", "/runs")],
        ),
        _nav_item("Reports", "/reports"),
    ]
    result = build_navigation(
        route_prefix="",
        navigation=navigation,
        active_path="/",
        request=_visibility_request(),
        visibility_resolver=_visibility_denied({"/", "/runs"}),
    )
    assert [item["path"] for item in result] == ["/reports"]


def test_build_navigation_mixed_nested_filtering() -> None:
    from beeui_module.pages.router import build_navigation

    navigation = [
        _nav_item(
            "Group A",
            children=[_nav_item("Leaf 1", "/a1"), _nav_item("Leaf 2", "/a2")],
        ),
        _nav_item("Group B", children=[_nav_item("Leaf 3", "/b3")]),
        _nav_item("Standalone", "/standalone"),
    ]
    result = build_navigation(
        route_prefix="",
        navigation=navigation,
        active_path="/standalone",
        request=_visibility_request(),
        visibility_resolver=_visibility_denied({"/a2", "/b3"}),
    )
    assert len(result) == 2
    assert result[0]["path"] is None
    assert [child["path"] for child in result[0]["children"]] == ["/a1"]
    assert result[1]["path"] == "/standalone"


def test_build_navigation_active_state_correct_with_hidden_active_item() -> None:
    from beeui_module.pages.router import build_navigation

    navigation = [
        _nav_item(
            "Workspace",
            children=[_nav_item("Dashboard", "/"), _nav_item("Runs", "/runs")],
        ),
        _nav_item("Reports", "/reports"),
    ]
    result = build_navigation(
        route_prefix="",
        navigation=navigation,
        active_path="/runs",
        request=_visibility_request(),
        visibility_resolver=_visibility_denied({"/runs"}),
    )
    assert [child["path"] for child in result[0]["children"]] == ["/"]
    assert result[0]["active"] is False
    assert result[0]["descendant_active"] is False
    assert result[1]["path"] == "/reports"
    assert all(not item["active"] for item in result)


def test_build_navigation_descendant_active_remains_correct() -> None:
    from beeui_module.pages.router import build_navigation

    navigation = [
        _nav_item("Workspace", children=[_nav_item("Runs", "/runs")]),
    ]
    result = build_navigation(
        route_prefix="",
        navigation=navigation,
        active_path="/runs",
        request=_visibility_request(),
        visibility_resolver=_visibility_denied(set()),
    )
    assert len(result) == 1
    assert result[0]["descendant_active"] is True
    assert result[0]["children"][0]["active"] is True


def test_build_navigation_failing_resolver_hides_item() -> None:
    from beeui_module.pages.router import build_navigation

    def failing_resolver(request, path):
        if path == "/runs":
            raise RuntimeError("resolver failure")
        return True

    navigation = [
        _nav_item("Dashboard", "/"),
        _nav_item("Runs", "/runs"),
    ]
    result = build_navigation(
        route_prefix="",
        navigation=navigation,
        active_path="/",
        request=_visibility_request(),
        visibility_resolver=failing_resolver,
    )
    assert [item["path"] for item in result] == ["/"]


def test_build_navigation_resolver_preserves_route_prefix_and_lang() -> None:
    from beeui_module.pages.router import build_navigation

    navigation = [
        _nav_item("Dashboard", "/"),
        _nav_item("Runs", "/runs"),
    ]
    result = build_navigation(
        route_prefix="/bee",
        navigation=navigation,
        active_path="/",
        locale="ru",
        default_locale="en",
        request=_visibility_request(),
        visibility_resolver=_visibility_denied(set()),
    )
    assert result[0]["href"] == "/bee?lang=ru"
    assert result[1]["href"] == "/bee/runs?lang=ru"


def test_configured_pages_use_request_scoped_navigation_resolver(
    tmp_path: Path,
) -> None:
    def request_scoped_resolver(request, path):
        return not (path == "/runs" and request.query_params.get("mode") == "basic")

    app = create_beeui_app(
        config_path=str(_visibility_schema(tmp_path)),
        navigation_visibility_resolver=request_scoped_resolver,
    )
    client = TestClient(app)

    default_response = client.get("/")
    assert default_response.status_code == 200
    assert 'href="/runs"' in default_response.text

    basic_response = client.get("/?mode=basic")
    assert basic_response.status_code == 200
    assert 'href="/runs"' not in basic_response.text
    assert 'href="/"' in basic_response.text


def test_configured_pages_resolver_preserves_route_prefix(tmp_path: Path) -> None:
    settings = load_settings(settings_path())
    settings["web"]["route_prefix"] = "/bee"

    app = create_beeui_app(
        settings=settings,
        config_path=str(_visibility_schema(tmp_path)),
        navigation_visibility_resolver=_visibility_denied({"/runs"}),
    )
    client = TestClient(app)

    response = client.get("/bee/")
    assert response.status_code == 200
    assert 'href="/bee/"' in response.text
    assert 'href="/bee/runs"' not in response.text


def test_configured_pages_resolver_preserves_lang(tmp_path: Path) -> None:
    app = create_beeui_app(
        config_path=str(_visibility_schema(tmp_path)),
        navigation_visibility_resolver=_visibility_denied(set()),
    )
    client = TestClient(app)

    response = client.get("/?lang=ru")
    assert response.status_code == 200
    assert 'href="/?lang=ru"' in response.text
    assert 'href="/runs?lang=ru"' in response.text


def test_configured_pages_failing_resolver_does_not_expose_items(
    tmp_path: Path,
) -> None:
    def failing_resolver(request, path):
        if path == "/runs":
            raise RuntimeError("resolver failure")
        return True

    app = create_beeui_app(
        config_path=str(_visibility_schema(tmp_path)),
        navigation_visibility_resolver=failing_resolver,
    )
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert 'href="/runs"' not in response.text
    assert 'href="/"' in response.text


def test_navigation_visibility_keeps_html_escaping(tmp_path: Path) -> None:
    settings = load_settings(settings_path())
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
        "      enabled: false\n"
        "      variant: default\n"
        "      sticky: false\n"
        "\n"
        "navigation:\n"
        "  - title: Dashboard\n"
        "    path: /\n"
        "    icon: dashboard\n"
        '  - title: "<script>alert(1)</script>"\n'
        "    path: /runs\n"
        "    icon: runs\n"
        "\n"
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
        "  - id: runs\n"
        "    path: /runs\n"
        "    title: Runs\n"
        "    subtitle: Runs page\n"
        "    blocks: []\n",
        encoding="utf-8",
    )

    app = create_beeui_app(
        settings=settings,
        config_path=str(schema_path),
        navigation_visibility_resolver=_visibility_denied(set()),
    )
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "<script>alert(1)</script>" not in response.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in response.text


def test_detail_page_uses_navigation_visibility_resolver() -> None:
    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    request = _visibility_request(
        _visibility_denied({"/runs"}),
        path="/detail",
    )

    response = render_beeui_detail_page(
        request=request,
        page={"page_id": "test", "title": "Test", "sections": []},
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = bytes(response.body).decode("utf-8")
    assert 'href="/runs"' not in body
    assert 'href="/"' in body


def test_create_beeui_app_rejects_non_callable_resolver() -> None:
    from typing import Any, cast

    settings = load_settings(settings_path())
    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    try:
        create_beeui_app(
            settings=settings,
            ui_config=ui_config,
            navigation_visibility_resolver=cast(Any, "not-callable"),
        )
    except ValueError as exc:
        assert "navigation_visibility_resolver" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-callable resolver")
