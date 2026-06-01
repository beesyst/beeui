from __future__ import annotations

from pathlib import Path

from beeui_module.pages.config import load_beeui_config


# Создание временного schema.yml для негативных проверок
def _write_schema(tmp_path: Path, content: str) -> Path:
    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(content, encoding="utf-8")
    return schema_path


# Возврат базовую demo schema как источник валидных defaults.
def _base_schema() -> str:
    return Path("config/schema.yml").read_text(encoding="utf-8")


# Тест: block id должен быть безопасным schema identifier
def test_schema_rejects_invalid_block_id(tmp_path: Path) -> None:
    base = _base_schema()
    invalid = base.replace("  latest_run:", "  Latest Run:", 1)

    try:
        load_beeui_config(_write_schema(tmp_path, invalid))
    except ValueError as exc:
        assert str(exc) == "blocks.Latest Run must be a safe identifier"
    else:
        raise AssertionError("load_beeui_config must reject unsafe block id")


# Тест: renderer-specific поля должны валидироваться внутри renderer contract
def test_schema_rejects_invalid_renderer_specific_field(tmp_path: Path) -> None:
    base = _base_schema()
    invalid = base.replace(
        "  runtime_status:\n    type: status_card\n    title: Runtime\n    status: ok\n    value: Ready\n",
        "  runtime_status:\n    type: status_card\n    title: Runtime\n    status: critical\n    value: Ready\n",
        1,
    )

    try:
        load_beeui_config(_write_schema(tmp_path, invalid))
    except ValueError as exc:
        assert (
            str(exc)
            == "blocks.runtime_status.status must be one of ['degraded', 'disabled', 'error', 'ok', 'partial', 'unavailable', 'unknown', 'warning']"
        )
    else:
        raise AssertionError(
            "load_beeui_config must reject invalid status_card status value"
        )


# Тест: display values принимают scalar literals и нормализуются в строки
def test_schema_accepts_scalar_display_values(tmp_path: Path) -> None:
    schema = _base_schema()
    schema = schema.replace("    value: run_demo_001\n", "    value: 42\n", 1)
    schema = schema.replace('        value: "24"\n', "        value: 24\n", 1)
    schema = schema.replace('        value: "1"\n', "        value: 1.5\n", 1)
    schema = schema.replace("    value: Ready\n", "    value: true\n", 1)

    config = load_beeui_config(_write_schema(tmp_path, schema))

    assert config.blocks["latest_run"].payload["value"] == "42"
    assert config.blocks["run_kpis"].payload["items"][0]["value"] == "24"
    assert config.blocks["run_kpis"].payload["items"][1]["value"] == "1.5"
    assert config.blocks["runtime_status"].payload["value"] == "True"


# Тест: display values не принимают вложенные objects/lists
def test_schema_rejects_nested_display_values(tmp_path: Path) -> None:
    invalid_values = [
        (
            "    value: run_demo_001\n",
            "    value:\n      nested: bad\n",
            "blocks.latest_run.value must be a scalar value",
        ),
        (
            '        value: "24"\n',
            "        value:\n          nested: bad\n",
            "blocks.run_kpis.items[0].value must be a scalar value",
        ),
        (
            "    value: Ready\n",
            "    value:\n      - bad\n",
            "blocks.runtime_status.value must be a scalar value",
        ),
    ]

    for old, new, expected_error in invalid_values:
        schema = _base_schema().replace(old, new, 1)

        try:
            load_beeui_config(_write_schema(tmp_path, schema))
        except ValueError as exc:
            assert str(exc) == expected_error
        else:
            raise AssertionError("load_beeui_config must reject nested display values")


# Тест: HTML/CSS/JS-подобные keys запрещены во всех block definitions
def test_schema_rejects_forbidden_block_keys(tmp_path: Path) -> None:
    base = _base_schema()
    forbidden_keys = [
        "html",
        "script",
        "javascript",
        "style",
        "css",
        "custom_css",
        "custom_js",
    ]

    for forbidden_key in forbidden_keys:
        invalid = base.replace(
            "  latest_run:\n    type: metric_card\n    title: Latest Run\n    value: run_demo_001\n    subtitle: Static demo value\n",
            "  latest_run:\n"
            "    type: metric_card\n"
            "    title: Latest Run\n"
            "    value: run_demo_001\n"
            "    subtitle: Static demo value\n"
            f"    {forbidden_key}: '<b>bad</b>'\n",
            1,
        )

        try:
            load_beeui_config(_write_schema(tmp_path, invalid))
        except ValueError as exc:
            assert str(exc) == (
                f"blocks.latest_run contains unsupported keys: {forbidden_key}"
            )
        else:
            raise AssertionError(
                f"load_beeui_config must reject forbidden {forbidden_key} key in block"
            )


# Тест: Top-level blocks обязан быть mapping, а не list/null/scalar
def test_schema_rejects_non_mapping_blocks_root(tmp_path: Path) -> None:
    invalid = (
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
        "      - title: Dashboard\n"
        "        path: /\n"
        "        icon: dashboard\n"
        "\n"
        "blocks: []\n"
        "\n"
        "pages:\n"
        "  - id: dashboard\n"
        "    path: /\n"
        "    title: Dashboard\n"
        "    subtitle: Demo\n"
        "    blocks: []\n"
    )

    try:
        load_beeui_config(_write_schema(tmp_path, invalid))
    except ValueError as exc:
        assert str(exc) == "blocks must be a mapping"
    else:
        raise AssertionError("load_beeui_config must reject non-mapping blocks root")


# Тест: table_card rows принимают только scalar values для безопасного вывода
def test_schema_rejects_invalid_table_rows_value(tmp_path: Path) -> None:
    base = _base_schema()
    invalid = base.replace(
        "      - id: run_demo_001\n        status: ok\n",
        "      - id: run_demo_001\n        status:\n          nested: bad\n",
        1,
    )

    try:
        load_beeui_config(_write_schema(tmp_path, invalid))
    except ValueError as exc:
        assert str(exc) == "blocks.recent_runs.rows[0].status must be a scalar value"
    else:
        raise AssertionError(
            "load_beeui_config must reject non-scalar table row values"
        )


# Тест: links_card не принимает внешние URL и опасные URL schemes
def test_schema_rejects_unsafe_links_card_hrefs(tmp_path: Path) -> None:
    base = _base_schema()
    unsafe_hrefs = [
        "http://example.com",
        "https://example.com",
        "//example.com/path",
        "mailto:test@example.com",
        "javascript:alert(1)",
    ]

    for unsafe_href in unsafe_hrefs:
        invalid = base.replace(
            "      - label: Open runs\n        href: /runs\n",
            f"      - label: Open runs\n        href: {unsafe_href}\n",
            1,
        )

        try:
            load_beeui_config(_write_schema(tmp_path, invalid))
        except ValueError as exc:
            assert str(exc) in {
                "blocks.quick_links.links[0].href must be an internal path",
                "blocks.quick_links.links[0].href must be a safe path",
            }
        else:
            raise AssertionError(
                f"load_beeui_config must reject unsafe links_card href {unsafe_href}"
            )
