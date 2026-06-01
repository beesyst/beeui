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
            "        path: /runs\n        icon: list\n",
            "        path: /missing\n        icon: list\n",
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
            "        path: /runs\n        icon: list\n",
            "        path: https://example.com\n        icon: list\n",
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


def test_load_beeui_config_fails_on_missing_top_level_blocks(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            'blocks:\n  latest_run:\n    type: metric_card\n    title: Latest Run\n    value: run_demo_001\n    subtitle: Static demo value\n\n  runtime_status:\n    type: status_card\n    title: Runtime\n    status: ok\n    value: Ready\n\n  run_kpis:\n    type: kpi_grid\n    title: Session KPIs\n    items:\n      - label: Total runs\n        value: "24"\n        status: ok\n      - label: Failed\n        value: "1"\n        status: warning\n\n  quick_links:\n    type: links_card\n    title: Quick links\n    links:\n      - label: Open runs\n        href: /runs\n\n  notice:\n    type: alert_card\n    title: Demo mode\n    message: Values are static and intended for UI contract validation.\n    severity: info\n\n  summary_text:\n    type: text_card\n    title: Summary\n    text: BeeUI renders reusable schema blocks with safe escaping.\n\n  completion:\n    type: progress_card\n    title: Bootstrap progress\n    value: 68\n    label: Iteration 5 in progress\n\n  recent_runs:\n    type: table_card\n    title: Recent runs\n    columns:\n      - key: id\n        label: Run ID\n      - key: status\n        label: Status\n    rows:\n      - id: run_demo_001\n        status: ok\n      - id: run_demo_002\n        status: partial\n\n',
            "",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "blocks must be a mapping"
    else:
        raise AssertionError(
            "load_beeui_config must fail when root blocks key is missing"
        )


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
            "        path: /runs\n        icon: list\n",
            "        path: /health\n        icon: list\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /health path")


# Тест: /static зарезервирован и не может быть page/navigation path
def test_load_beeui_config_rejects_reserved_static_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _base_config().replace(
            "        path: /runs\n        icon: list\n",
            "        path: /static\n        icon: list\n",
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
            "        path: /runs\n        icon: list\n",
            "        path: /static/css/beeui.css\n        icon: list\n",
            1,
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /static/... path")
