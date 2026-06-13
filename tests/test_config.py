from __future__ import annotations

from pathlib import Path

from beeui_module.pages.config import load_beeui_config


# Тесты для проверки загрузки и валидации конфигурации BeeUI, включая проверку обязательных полей, типов данных, допустимых значений и ссылок на страницы и блоки
def _base_config() -> str:
    return Path("config/schema.yml").read_text(encoding="utf-8")


# Запись временного конфигурационного файла с заданным содержимым
def _write_config(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "schema.yml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


# Тест: валидная demo schema загружается вместе с Iteration 5 blocks
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


# Тест: app.title обязателен и валидируется fail-fast
def test_load_beeui_config_fails_on_missing_app_title(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace("  title: BeeUI Demo\n", "", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "app.title must be a non-empty string"
    else:
        raise AssertionError("load_beeui_config must fail on missing app.title")


# Тест: theme.mode принимает только разрешённые значения
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


# Тест: page.id должен быть уникальным
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


# Тест: page.path должен быть уникальным
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


# Тест: navigation path должен ссылаться на объявленную страницу
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


# Тест: external navigation path запрещён в текущем schema contract
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


# Тест: pages[].blocks обязателен и должен быть list
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


# Тест: корневой ключ blocks обязателен и должен быть mapping
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


# Тест: корневой ключ blocks должен быть mapping, а не list или scalar
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


# Тест: block source ссылается на несуществующий data source, load_beeui_config должен отклонить конфигурацию с ошибкой
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


# Тест: invalid data source type должен быть отклонён с ошибкой валидации
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


# Тест: /health зарезервирован и не может быть page/navigation path
def test_load_beeui_config_rejects_reserved_health_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: runs\n",
            "        path: /health\n        icon: runs\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /health path")


# Тест: /components зарезервирован для internal component catalog
def test_load_beeui_config_rejects_reserved_components_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: runs\n",
            "        path: /components\n        icon: runs\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /components path")


# Тест: /components/... зарезервирован для internal component catalog
def test_load_beeui_config_rejects_reserved_components_prefix(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: runs\n",
            "        path: /components/forms\n        icon: runs\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError(
            "load_beeui_config must reject reserved /components/... path"
        )


# Тест: /static зарезервирован и не может быть page/navigation path
def test_load_beeui_config_rejects_reserved_static_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: runs\n",
            "        path: /static\n        icon: runs\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /static path")


# Тест: /static/... зарезервирован для package-local assets
def test_load_beeui_config_rejects_reserved_static_prefix(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: runs\n",
            "        path: /static/css/beeui.css\n        icon: runs\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /static/... path")


# Тест: pages[].blocks[] принимает {id, enabled} page block ref
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


# Тест: pages[].blocks[] принимает {id} без enabled
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


# Тест: pages[].blocks[] отвергает неизвестные ключи в {id, enabled}
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


# Тест: pages[].blocks[] отвергает не-string id
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


# Тест: pages[].blocks[] отвергает не-bool enabled
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


# Тест: pages[].blocks[] принимает {id} без top-level block definition
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


# Тест: pages[].blocks[] отвергает небезопасный id
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


# Тест: regression — исходная ошибка pages[0].blocks[0] содержит unsupported keys: enabled, id
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


# Тест: существующий {block, width} placement всё ещё работает
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


# Тест: source config file content не меняется после load_beeui_config
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


# Тест: .beeui_sanitized.yml не создаётся
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


# Тест: app factory стартует с config содержащим {id, enabled} page blocks
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


# Тест: BeeCap-like config с product page refs и пустым blocks: {}
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


# Тест: span в schema placement работает
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


# Тест: size в schema placement работает
def test_schema_accepts_size_placement(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        size: L\n",
        1,
    )
    config = load_beeui_config(_write_config(tmp_path, content))
    dashboard = config.pages[0]
    assert dashboard.blocks[0].size == "L"


# Тест: size case-insensitive в schema
def test_schema_accepts_size_lowercase(tmp_path: Path) -> None:
    content = _base_config().replace(
        "      - block: latest_run\n        width: 3\n",
        "      - block: latest_run\n        size: xl\n",
        1,
    )
    config = load_beeui_config(_write_config(tmp_path, content))
    dashboard = config.pages[0]
    assert dashboard.blocks[0].size == "XL"


# Тест: конфликтующие sizing keys в schema placement fail fast
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


# Тест: невалидный span в schema placement fail fast
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


# Тест: невалидный size в schema placement fail fast
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


# Тест: locale default en без config
def test_schema_locale_default() -> None:
    config = load_beeui_config(Path("config/schema.yml"))
    assert config.locale.default == "en"
    assert "ru" in config.locale.available


# Тест: locale config работает
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


# Тест: locale default вне available fail fast
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
        raise AssertionError("load_beeui_config must reject locale default not in available")
