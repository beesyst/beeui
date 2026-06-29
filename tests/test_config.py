from __future__ import annotations

from pathlib import Path

from beeui_module.pages.config import (
    is_custom_route_reserved_path,
    load_beeui_config,
)


def _base_config() -> str:
    return Path("config/schema.yml").read_text(encoding="utf-8")


def _write_config(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "schema.yml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


def _collect_nav_paths(items: list) -> set[str]:
    paths: set[str] = set()
    for item in items:
        if item.path:
            paths.add(item.path)
        if item.children:
            paths |= _collect_nav_paths(item.children)
    return paths


def test_load_beeui_config_valid_payload() -> None:
    config = load_beeui_config(Path("config/schema.yml"))

    assert config.app_title == "BeeUI Demo"
    assert config.product == "demo"
    assert config.logo_text == "BeeUI"
    assert config.theme.mode == "dark"
    assert config.layout.container == "xl"
    assert [page.path for page in config.pages] == ["/", "/runs"]
    assert config.data_sources["demo_dashboard"].source_type == "demo"
    assert "latest_run" in config.blocks
    assert "runtime_status" in config.blocks


def test_load_beeui_config_fails_on_missing_app_title(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("  title: BeeUI Demo\n", "", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert "app.title must be a string or a mapping" in str(exc)
    else:
        raise AssertionError("load_beeui_config must fail on missing app.title")


def test_load_beeui_config_rejects_invalid_theme_mode(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("mode: dark", "mode: neon", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "app.theme.mode must be one of ['auto', 'dark', 'light']"
    else:
        raise AssertionError("load_beeui_config must fail on invalid theme mode")


def test_load_beeui_config_rejects_arbitrary_css_js_html_keys(tmp_path: Path) -> None:
    forbidden_keys = [
        "custom_css",
        "css",
        "style",
        "custom_js",
        "script",
        "javascript",
        "html",
    ]

    for forbidden_key in forbidden_keys:
        config_path = _write_config(
            tmp_path,
            _base_config().replace(
                "  theme:\n",
                f"  {forbidden_key}: injected\n  theme:\n",
                1,
            ),
        )

        try:
            load_beeui_config(config_path)
        except ValueError as exc:
            assert str(exc) == f"app contains unsupported keys: {forbidden_key}"
        else:
            raise AssertionError(
                f"load_beeui_config must reject arbitrary key {forbidden_key}"
            )


def test_load_beeui_config_fails_on_duplicate_page_id(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("id: runs", "id: dashboard", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "Duplicate page id: dashboard"
    else:
        raise AssertionError("load_beeui_config must fail on duplicate page id")


def test_load_beeui_config_fails_on_duplicate_page_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "  - id: runs\n    path: /runs\n",
            "  - id: runs\n    path: /\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "Duplicate page path: /"
    else:
        raise AssertionError("load_beeui_config must fail on duplicate page path")


def test_load_beeui_config_fails_on_unknown_navigation_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: runs\n",
            "        path: /missing\n        icon: runs\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation path must match a declared page path: /missing"
    else:
        raise AssertionError("load_beeui_config must fail on unknown navigation path")


def test_load_beeui_config_rejects_external_navigation_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: runs\n",
            "        path: https://example.com\n        icon: runs\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path must start with '/'"
    else:
        raise AssertionError("load_beeui_config must reject external navigation path")


def test_load_beeui_config_fails_on_missing_page_blocks(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "    blocks:\n      - block: latest_run\n        width: 3\n      - block: runtime_status\n        width: 3\n      - block: completion\n        width: 3\n      - block: quick_links\n        width: 3\n      - block: run_kpis\n        width: 6\n      - block: notice\n        width: 6\n      - block: recent_runs\n        width: 8\n      - block: summary_text\n        width: 4\n",
            "",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[0].blocks must be a list"
    else:
        raise AssertionError(
            "load_beeui_config must fail when page blocks key is missing"
        )


def test_load_beeui_config_fails_on_missing_top_level_blocks(tmp_path: Path) -> None:
    base = _base_config()
    start = base.index("blocks:\n")
    end = base.index("\npages:\n")
    config_path = _write_config(tmp_path, f"{base[:start]}{base[end + 1 :]}")

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "blocks must be a mapping"
    else:
        raise AssertionError(
            "load_beeui_config must fail when root blocks key is missing"
        )


def test_load_beeui_config_accepts_optional_data_sources_section(
    tmp_path: Path,
) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config()
        .replace(
            "data_sources:\n  demo_dashboard:\n    type: demo\n\n",
            "",
            1,
        )
        .replace(
            "    source: demo_dashboard\n    value_selector: dashboard.latest_run.id\n    subtitle_selector: dashboard.latest_run.status\n",
            "    value: run_demo_001\n    subtitle: Static demo value\n",
            1,
        )
        .replace(
            "    source: demo_dashboard\n    status_selector: dashboard.runtime.status\n    value_selector: dashboard.runtime.value\n",
            "    status: ok\n    value: Ready\n",
            1,
        )
        .replace(
            "    source: demo_dashboard\n    items_selector: dashboard.kpi_items\n",
            '    items:\n      - label: Total runs\n        value: "24"\n        status: ok\n      - label: Failed\n        value: "1"\n        status: warning\n',
            1,
        )
        .replace(
            "    source: demo_dashboard\n    text_selector: dashboard.summary.text\n",
            "    text: BeeUI renders reusable schema blocks with safe escaping.\n",
            1,
        )
        .replace(
            "    source: demo_dashboard\n    rows_selector: runs\n",
            "    rows:\n      - id: run_demo_001\n        status: ok\n      - id: run_demo_002\n        status: partial\n",
            1,
        ),
    )

    config = load_beeui_config(config_path)

    assert config.data_sources == {}
    assert config.blocks["latest_run"].payload["value"] == "run_demo_001"


def test_load_beeui_config_rejects_unknown_block_source(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "source: demo_dashboard",
            "source: missing_dashboard",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert (
            str(exc)
            == "blocks.latest_run.source references an unknown data source: missing_dashboard"
        )
    else:
        raise AssertionError("load_beeui_config must reject unknown block source")


def test_load_beeui_config_rejects_invalid_data_source_type(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("    type: demo\n", "    type: invalid\n", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert (
            str(exc)
            == "data_sources.demo_dashboard.type must be one of ['demo', 'static']"
        )
    else:
        raise AssertionError("load_beeui_config must reject invalid data source type")


def test_load_beeui_config_rejects_unsafe_static_source_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config()
        .replace(
            "data_sources:\n  demo_dashboard:\n    type: demo\n\n",
            "data_sources:\n  static_dashboard:\n    type: static\n    format: yaml\n    path: ../secrets.yml\n\n",
            1,
        )
        .replace("source: demo_dashboard", "source: static_dashboard"),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert (
            str(exc)
            == "data_sources.static_dashboard.path must be a safe relative path"
        )
    else:
        raise AssertionError("load_beeui_config must reject unsafe static source path")


def test_load_beeui_config_fails_on_unknown_block_reference(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("block: completion", "block: missing_block", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "Unknown block reference: missing_block"
    else:
        raise AssertionError("load_beeui_config must fail on unknown block reference")


def test_load_beeui_config_fails_on_unknown_block_type(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("type: metric_card", "type: unknown_card", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert (
            str(exc)
            == "blocks.latest_run.type must be one of ['alert_card', 'kpi_grid', 'links_card', 'metric_card', 'progress_card', 'status_card', 'table_card', 'text_card']"
        )
    else:
        raise AssertionError("load_beeui_config must fail on unknown block type")


def test_load_beeui_config_fails_on_invalid_block_width(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("width: 3", "width: 13", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[0].blocks[0].width must be an integer in range 1..12"
    else:
        raise AssertionError("load_beeui_config must fail on invalid block width")


def test_load_beeui_config_rejects_external_links_in_links_card(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - label: Open runs\n        href: /runs\n",
            "      - label: Open runs\n        href: https://example.com\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "blocks.quick_links.links[0].href must be an internal path"
    else:
        raise AssertionError(
            "load_beeui_config must fail on external links in links_card"
        )


def test_load_beeui_config_rejects_navigation_path_without_matching_page(
    tmp_path: Path,
) -> None:
    for path in (
        "/health",
        "/api",
        "/auth",
        "/venues",
        "/modes",
        "/login",
        "/logout",
        "/static",
        "/components",
    ):
        config_path = _write_config(
            tmp_path,
            _base_config().replace(
                "        path: /runs\n        icon: runs\n",
                f"        path: {path}\n        icon: runs\n",
                1,
            ),
        )

        try:
            load_beeui_config(config_path)
        except ValueError as exc:
            assert (
                str(exc) == f"navigation path must match a declared page path: {path}"
            )
        else:
            raise AssertionError(
                f"load_beeui_config must reject navigation path {path} without matching page"
            )


def test_load_beeui_config_accepts_page_route_modes(tmp_path: Path) -> None:
    for mode in ("metadata", "adapter", "configured"):
        config_path = _write_config(
            tmp_path,
            _base_config().replace(
                "  - id: runs\n    path: /runs\n",
                f"  - id: runs\n    path: /runs\n    route:\n      mode: {mode}\n",
                1,
            ),
        )

        config = load_beeui_config(config_path)
        assert config.pages[1].route.mode == mode


def test_load_beeui_config_rejects_unknown_page_route_mode(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "  - id: runs\n    path: /runs\n",
            "  - id: runs\n    path: /runs\n    route:\n      mode: python\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert (
            str(exc)
            == "pages[1].route.mode must be one of: adapter, configured, metadata"
        )
    else:
        raise AssertionError("load_beeui_config must reject unknown page route mode")


def test_load_beeui_config_rejects_unknown_page_route_keys(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "  - id: runs\n    path: /runs\n",
            "  - id: runs\n    path: /runs\n"
            "    route:\n"
            "      mode: metadata\n"
            "      handler: python.module.callable\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[1].route contains unsupported keys: handler"
    else:
        raise AssertionError("load_beeui_config must reject arbitrary route keys")


def test_load_beeui_config_accepts_nested_safe_page_paths(
    tmp_path: Path,
) -> None:
    for page_path in (
        "/venues/mrkt",
        "/modes/live",
        "/hidra/binance",
        "/likes/top",
    ):
        config_path = _write_config(
            tmp_path,
            _base_config().replace(
                "    subtitle: Placeholder page for future run overview\n    blocks: []\n",
                f"    subtitle: Placeholder page for future run overview\n    blocks: []\n"
                f"  - id: meta\n    path: {page_path}\n"
                f"    title: Metadata\n    subtitle: Console ref\n    blocks: []\n",
                1,
            ),
        )

        config = load_beeui_config(config_path)
        page_paths = [p.path for p in config.pages]
        assert page_path in page_paths
        assert "/" in page_paths
        assert "/runs" in page_paths


def test_load_beeui_config_accepts_nested_safe_navigation_paths(
    tmp_path: Path,
) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config()
        .replace(
            "    subtitle: Placeholder page for future run overview\n    blocks: []\n",
            "    subtitle: Placeholder page for future run overview\n    blocks: []\n"
            "  - id: mrkt_meta\n    path: /venues/mrkt\n"
            "    title: MRKT\n    subtitle: Venue\n    blocks: []\n"
            "  - id: mode_live\n    path: /modes/live\n"
            "    title: Live\n    subtitle: Mode\n    blocks: []\n"
            "  - id: hidra_binance\n    path: /hidra/binance\n"
            "    title: Hidra Binance\n    subtitle: Adapter page\n    blocks: []\n"
            "  - id: likes_top\n    path: /likes/top\n"
            "    title: Likes\n    subtitle: Configured page\n    blocks: []\n",
            1,
        )
        .replace(
            "        path: /runs\n        icon: runs\n",
            "        path: /runs\n        icon: runs\n"
            "      - title: MRKT\n        path: /venues/mrkt\n        icon: venue\n"
            "      - title: Live\n        path: /modes/live\n        icon: mode\n"
            "      - title: Hidra Binance\n        path: /hidra/binance\n        icon: venue\n"
            "      - title: Likes\n        path: /likes/top\n        icon: list\n",
            1,
        ),
    )

    config = load_beeui_config(config_path)
    nav_paths = _collect_nav_paths(config.navigation)
    assert "/venues/mrkt" in nav_paths
    assert "/modes/live" in nav_paths
    assert "/hidra/binance" in nav_paths
    assert "/likes/top" in nav_paths


def test_is_custom_route_reserved_exact_paths() -> None:
    reserved = [
        "/health",
        "/api",
        "/auth",
        "/login",
        "/logout",
        "/static",
        "/components",
    ]
    for path in reserved:
        assert is_custom_route_reserved_path(path), f"{path} must be reserved"


def test_is_custom_route_reserved_prefix_paths() -> None:
    reserved = [
        "/api/debug",
        "/auth/test",
        "/static/css/beeui.css",
        "/components/forms",
    ]
    for path in reserved:
        assert is_custom_route_reserved_path(path), f"{path} must be reserved"


def test_is_custom_route_reserved_non_reserved_paths() -> None:
    non_reserved = [
        "/rop",
        "/modules",
        "/reports",
        "/settings-lite",
        "/venues",
        "/venues/mrkt",
        "/modes",
        "/modes/dry-run",
        "/modes/paper",
        "/modes/live",
        "/hidra/binance",
        "/likes/top",
        "/runs",
        "/runs/run_001",
    ]
    for path in non_reserved:
        assert not is_custom_route_reserved_path(path), f"{path} must not be reserved"


def test_load_beeui_config_rejects_nav_paths_to_system_routes_without_page(
    tmp_path: Path,
) -> None:
    for path in (
        "/components",
        "/components/forms",
        "/static",
        "/static/css/beeui.css",
        "/auth/csrf",
    ):
        config_path = _write_config(
            tmp_path,
            _base_config().replace(
                "        path: /runs\n        icon: runs\n",
                f"        path: {path}\n        icon: runs\n",
                1,
            ),
        )

        try:
            load_beeui_config(config_path)
        except ValueError as exc:
            assert (
                str(exc) == f"navigation path must match a declared page path: {path}"
            )
        else:
            raise AssertionError(
                f"load_beeui_config must reject nav path {path} without matching page"
            )


def test_page_block_ref_id_enabled_accepted(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - block: latest_run\n        width: 3\n",
            "      - id: latest_run\n        enabled: true\n",
            1,
        ),
    )

    config = load_beeui_config(config_path)

    assert len(config.pages) == 2
    dashboard = config.pages[0]
    assert len(dashboard.blocks) == 8
    assert dashboard.blocks[0].block_id == "latest_run"
    assert dashboard.blocks[0].width == 12


def test_page_block_ref_id_only_accepted(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - block: latest_run\n        width: 3\n",
            "      - id: latest_run\n",
            1,
        ),
    )

    config = load_beeui_config(config_path)

    assert len(config.pages) == 2
    dashboard = config.pages[0]
    assert len(dashboard.blocks) == 8
    assert dashboard.blocks[0].block_id == "latest_run"
    assert dashboard.blocks[0].width == 12


def test_page_block_ref_extra_key_rejected(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - block: latest_run\n        width: 3\n",
            "      - id: latest_run\n        enabled: true\n        width: 6\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert (
            "must not mix placement keys (block, width) with reference keys (id, enabled)"
            in str(exc)
        )
    else:
        raise AssertionError(
            "load_beeui_config must reject page block ref with extra key"
        )


def test_page_block_ref_non_string_id_rejected(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - block: latest_run\n        width: 3\n",
            "      - id: 42\n        enabled: true\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[0].blocks[0].id must be a non-empty string"
    else:
        raise AssertionError(
            "load_beeui_config must reject page block ref with non-string id"
        )


def test_page_block_ref_non_bool_enabled_rejected(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - block: latest_run\n        width: 3\n",
            '      - id: latest_run\n        enabled: "yes"\n',
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[0].blocks[0].enabled must be a boolean"
    else:
        raise AssertionError(
            "load_beeui_config must reject page block ref with non-bool enabled"
        )


def test_page_block_ref_unknown_product_id_is_accepted(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - block: latest_run\n        width: 3\n",
            "      - id: system_snapshot\n        enabled: true\n",
            1,
        ),
    )

    config = load_beeui_config(config_path)

    assert len(config.pages) == 2
    dashboard = config.pages[0]
    assert len(dashboard.blocks) == 8
    assert dashboard.blocks[0].block_id == "system_snapshot"
    assert dashboard.blocks[0].width == 12


def test_page_block_ref_unsafe_id_rejected(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "      - block: latest_run\n        width: 3\n",
            "      - id: ../../evil\n        enabled: true\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[0].blocks[0].id must be a safe identifier"
    else:
        raise AssertionError(
            "load_beeui_config must reject page block ref with unsafe id"
        )


def test_page_block_ref_regression_original_error(tmp_path: Path) -> None:
    config_content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - id: latest_run\n        enabled: true\n",
        1,
    )
    config_path = _write_config(tmp_path, config_content)

    config = load_beeui_config(config_path)

    assert len(config.pages) == 2
    dashboard = config.pages[0]
    assert len(dashboard.blocks) == 8
    assert dashboard.blocks[0].block_id == "latest_run"


def test_existing_block_width_placement_still_works(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config(),
    )

    config = load_beeui_config(config_path)

    assert len(config.pages) == 2
    dashboard = config.pages[0]
    assert len(dashboard.blocks) >= 1
    assert dashboard.blocks[0].block_id == "latest_run"
    assert dashboard.blocks[0].width == 3


def test_page_block_ref_does_not_mutate_source_config(tmp_path: Path) -> None:
    config_content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - id: latest_run\n        enabled: true\n",
        1,
    )
    config_path = _write_config(tmp_path, config_content)
    original_content = config_path.read_text(encoding="utf-8")

    load_beeui_config(config_path)

    assert config_path.read_text(encoding="utf-8") == original_content


def test_page_block_ref_no_sanitized_yml_created(tmp_path: Path) -> None:
    config_content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - id: latest_run\n        enabled: true\n",
        1,
    )
    config_path = _write_config(tmp_path, config_content)

    load_beeui_config(config_path)

    sanitized = tmp_path / ".beeui_sanitized.yml"
    assert not sanitized.exists()


def test_app_factory_starts_with_id_enabled_page_block_refs(tmp_path: Path) -> None:
    from beeui_module.core.paths import settings_path
    from beeui_module.core.settings import load_settings
    from beeui_module.web.app import create_beeui_app

    settings = load_settings(settings_path())
    config_content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - id: latest_run\n        enabled: true\n",
        1,
    )
    config_path = _write_config(tmp_path, config_content)
    ui_config = load_beeui_config(config_path)

    app = create_beeui_app(settings=settings, ui_config=ui_config)

    assert app is not None


def test_page_block_ref_beecap_like_config(tmp_path: Path) -> None:
    config_content = (
        "app:\n"
        "  title: BeeCap\n"
        "  product: beecap\n"
        "  logo_text: BeeCap\n"
        "  theme:\n"
        "    mode: dark\n"
        "    primary: green\n"
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
        "  - title: BeeCap\n"
        "    children:\n"
        "      - title: Dashboard\n"
        "        path: /\n"
        "        icon: dashboard\n"
        "\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: BeeCap operator dashboard\n"
        "    blocks:\n"
        "      - id: system_snapshot\n"
        "        enabled: true\n"
        "      - id: venue_cards\n"
        "        enabled: true\n"
        "\n"
        "blocks: {}\n"
    )
    config_path = _write_config(tmp_path, config_content)

    config = load_beeui_config(config_path)

    assert config.app_title == "BeeCap"
    assert config.product == "beecap"
    assert len(config.pages) == 1
    dashboard = config.pages[0]
    assert len(dashboard.blocks) == 2
    assert dashboard.blocks[0].block_id == "system_snapshot"
    assert dashboard.blocks[1].block_id == "venue_cards"


def test_schema_accepts_span_placement(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        span: 4\n",
        1,
    )
    config = load_beeui_config(_write_config(tmp_path, content))
    dashboard = config.pages[0]
    assert dashboard.blocks[0].span == 4
    assert dashboard.blocks[0].width == 12


def test_schema_accepts_size_placement(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        size: L\n",
        1,
    )
    config = load_beeui_config(_write_config(tmp_path, content))
    dashboard = config.pages[0]
    assert dashboard.blocks[0].size == "L"


def test_schema_accepts_size_lowercase(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        size: xl\n",
        1,
    )
    config = load_beeui_config(_write_config(tmp_path, content))
    dashboard = config.pages[0]
    assert dashboard.blocks[0].size == "XL"


def test_schema_rejects_conflicting_sizing_keys(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        width: 6\n        span: 12\n",
        1,
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "must not mix sizing keys" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject conflicting sizing keys")


def test_schema_rejects_invalid_span(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        span: 99\n",
        1,
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "span must be an integer in range 1..12" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject invalid span")


def test_schema_rejects_invalid_size(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        size: XXL\n",
        1,
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "size must be one of S, M, L, XL" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject invalid size")


def test_schema_locale_default() -> None:
    config = load_beeui_config(Path("config/schema.yml"))
    assert config.locale.default == "en"
    assert "ru" in config.locale.available


def test_schema_locale_custom(tmp_path: Path) -> None:
    content = (
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
        "  locale:\n"
        "    default: ru\n"
        "    available:\n"
        "      - ru\n"
        "      - en\n"
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
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
    )
    config = load_beeui_config(_write_config(tmp_path, content))
    assert config.locale.default == "ru"
    assert config.locale.available == ("ru", "en")


def test_schema_locale_default_not_in_available(tmp_path: Path) -> None:
    content = (
        "app:\n"
        "  title: Test\n"
        "  product: test\n"
        "  logo_text: Test\n"
        "  locale:\n"
        "    default: de\n"
        "    available:\n"
        "      - en\n"
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
        "data_sources: {}\n"
        "blocks: {}\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "must be in app.locale.available" in str(exc)
    else:
        raise AssertionError(
            "load_beeui_config must reject locale default not in available"
        )


def _minimal_schema() -> str:
    return (
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
    )


def test_components_tabs_variant_valid(tmp_path: Path) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  tabs:\n    variant: fill\n\ndata_sources: {}\n",
        1,
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.components.tabs.variant == "fill"


def test_components_tabs_variant_numeric_alias_normalizes(tmp_path: Path) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  tabs:\n    variant: 4\n\ndata_sources: {}\n",
        1,
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.components.tabs.variant == "dropdown"


def test_components_tabs_variant_invalid_fails_fast(tmp_path: Path) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  tabs:\n    variant: bogus\n\ndata_sources: {}\n",
        1,
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "bogus" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject invalid tabs variant")


def test_components_tabs_variant_invalid_numeric_fails_fast(tmp_path: Path) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  tabs:\n    variant: 99\n\ndata_sources: {}\n",
        1,
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "99" in str(exc)
    else:
        raise AssertionError(
            "load_beeui_config must reject invalid numeric tabs variant"
        )


def test_components_accordion_variant_valid(tmp_path: Path) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  accordion:\n    variant: flush\n\ndata_sources: {}\n",
        1,
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.components.accordion.variant == "flush"


def test_components_accordion_variant_numeric_alias_normalizes(tmp_path: Path) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  accordion:\n    variant: 2\n\ndata_sources: {}\n",
        1,
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.components.accordion.variant == "flush"


def test_components_accordion_variant_invalid_fails_fast(tmp_path: Path) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  accordion:\n    variant: bogus\n\ndata_sources: {}\n",
        1,
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "bogus" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject invalid accordion variant")


def test_components_accordion_variant_invalid_numeric_fails_fast(
    tmp_path: Path,
) -> None:
    content = _minimal_schema().replace(
        "data_sources: {}\n",
        "components:\n  accordion:\n    variant: 99\n\ndata_sources: {}\n",
        1,
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "99" in str(exc)
    else:
        raise AssertionError(
            "load_beeui_config must reject invalid numeric accordion variant"
        )


def test_components_missing_uses_defaults(tmp_path: Path) -> None:
    cfg = load_beeui_config(_write_config(tmp_path, _minimal_schema()))
    assert cfg.components.tabs.variant == "default"
    assert cfg.components.accordion.variant == "default"


def _schema_with_page_tabs(page_tabs_yaml: str) -> str:
    return (
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
        f"{page_tabs_yaml}\n"
    )


def test_page_tabs_valid_config(tmp_path: Path) -> None:
    content = _schema_with_page_tabs(
        "  - id: rop\n"
        "    path: /rop\n"
        "    title: ROP\n"
        "    subtitle: ROP dashboard\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      variant: fill\n"
        "      active_param: tab\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /rop?tab=overview\n"
        "        - id: queue\n"
        "          title: Queue\n"
        "          href: /rop?tab=queue\n"
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    rop_page = cfg.pages[1]
    assert rop_page.tabs is not None
    assert rop_page.tabs.variant == "fill"
    assert rop_page.tabs.active_param == "tab"
    assert len(rop_page.tabs.items) == 2
    assert rop_page.tabs.items[0].tab_id == "overview"
    assert rop_page.tabs.items[1].href == "/rop?tab=queue"


def test_page_tabs_numeric_variant_alias_normalizes(tmp_path: Path) -> None:
    content = _schema_with_page_tabs(
        "  - id: rop\n"
        "    path: /rop\n"
        "    title: ROP\n"
        "    subtitle: ROP dashboard\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      variant: 5\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /rop?tab=overview\n"
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.pages[1].tabs is not None
    assert cfg.pages[1].tabs.variant == "fill"


def test_page_tabs_duplicate_ids_fail_fast(tmp_path: Path) -> None:
    content = _schema_with_page_tabs(
        "  - id: rop\n"
        "    path: /rop\n"
        "    title: ROP\n"
        "    subtitle: ROP dashboard\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /rop?tab=overview\n"
        "        - id: overview\n"
        "          title: Queue\n"
        "          href: /rop?tab=queue\n"
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "Duplicate tab id" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject duplicate tab ids")


def test_page_tabs_invalid_numeric_variant_fails_fast(tmp_path: Path) -> None:
    content = _schema_with_page_tabs(
        "  - id: rop\n"
        "    path: /rop\n"
        "    title: ROP\n"
        "    subtitle: ROP dashboard\n"
        "    blocks: []\n"
        "    tabs:\n"
        "      variant: 99\n"
        "      items:\n"
        "        - id: overview\n"
        "          title: Overview\n"
        "          href: /rop?tab=overview\n"
    )
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "99" in str(exc)
    else:
        raise AssertionError(
            "load_beeui_config must reject invalid numeric page tabs variant"
        )


def test_page_tabs_unsafe_href_rejected(tmp_path: Path) -> None:
    for unsafe_href in (
        "http://evil.com",
        "https://evil.com",
        "//evil.com",
        "javascript:alert(1)",
        "mailto:test@test.com",
    ):
        content = _schema_with_page_tabs(
            "  - id: rop\n"
            "    path: /rop\n"
            "    title: ROP\n"
            "    subtitle: ROP dashboard\n"
            "    blocks: []\n"
            "    tabs:\n"
            "      items:\n"
            "        - id: overview\n"
            "          title: Overview\n"
            f"          href: {unsafe_href}\n"
        )
        try:
            load_beeui_config(_write_config(tmp_path, content))
        except ValueError as exc:
            assert (
                "href must not" in str(exc)
                or "href must start" in str(exc)
                or "href must be an internal link" in str(exc)
            )
        else:
            raise AssertionError(
                f"load_beeui_config must reject unsafe href: {unsafe_href}"
            )


def _localized_schema_base(app_title_yaml: str, logo_text_yaml: str) -> str:
    return (
        "app:\n"
        f"  title: {app_title_yaml}\n"
        "  product: test\n"
        f"  logo_text: {logo_text_yaml}\n"
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
        "  - title: Nav\n"
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
    )


def test_localized_app_title_valid(tmp_path: Path) -> None:
    content = _localized_schema_base("{en: BeeUI, ru: БИУ}", "BeeUI")
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.app_title == {"en": "BeeUI", "ru": "БИУ"}
    assert cfg.logo_text == "BeeUI"


def test_localized_app_title_unknown_locale_key_fails(tmp_path: Path) -> None:
    content = _localized_schema_base("{en: BeeUI, fr: BeeUI}", "BeeUI")
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "unknown locale key" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject unknown locale key")


def test_localized_app_title_missing_default_fails(tmp_path: Path) -> None:
    content = _localized_schema_base("{ru: БИУ}", "BeeUI")
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "must contain default locale key" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject missing default locale")


def test_localized_app_title_empty_mapping_fails(tmp_path: Path) -> None:
    content = _localized_schema_base("{}", "BeeUI")
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject empty mapping")


def test_localized_app_title_non_string_value_fails(tmp_path: Path) -> None:
    content = _localized_schema_base("{en: 42, ru: БИУ}", "BeeUI")
    try:
        load_beeui_config(_write_config(tmp_path, content))
    except ValueError as exc:
        assert "non-empty string" in str(exc)
    else:
        raise AssertionError("load_beeui_config must reject non-string value")


def test_localized_page_title_valid(tmp_path: Path) -> None:
    content = _localized_schema_base("BeeUI", "BeeUI").replace(
        "    title: Dashboard\n",
        "    title:\n      en: Dashboard\n      ru: Дашборд\n",
        1,
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.pages[0].title == {"en": "Dashboard", "ru": "Дашборд"}


def test_localized_nav_title_valid(tmp_path: Path) -> None:
    content = _localized_schema_base("BeeUI", "BeeUI").replace(
        "  - title: Nav\n",
        "  - title:\n      en: Nav\n      ru: Нав\n",
        1,
    )
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.navigation[0].title == {"en": "Nav", "ru": "Нав"}


def test_existing_plain_string_config_still_works(tmp_path: Path) -> None:
    content = _localized_schema_base("BeeUI", "BeeUI")
    cfg = load_beeui_config(_write_config(tmp_path, content))
    assert cfg.app_title == "BeeUI"
    assert cfg.logo_text == "BeeUI"
    assert cfg.pages[0].title == "Dashboard"
    assert cfg.navigation[0].title == "Nav"
