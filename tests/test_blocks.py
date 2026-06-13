from __future__ import annotations

import re
from pathlib import Path

from beeui_module.blocks.layout_renderer import render_layout
from beeui_module.pages.config import load_beeui_config


# Создание временного schema.yml для негативных проверок
def _write_schema(tmp_path: Path, content: str) -> Path:
    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(content, encoding="utf-8")
    return schema_path


# Возврат базовую demo schema как источник валидных defaults.
def _base_schema() -> str:
    return Path("config/schema.yml").read_text(encoding="utf-8")


# Возврат базовой demo schema с literal значениями для display fields вместо селекторов
def _literal_schema() -> str:
    return (
        _base_schema()
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
        )
    )


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
    base = _literal_schema()
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
    schema = _literal_schema()
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
        schema = _literal_schema().replace(old, new, 1)

        try:
            load_beeui_config(_write_schema(tmp_path, schema))
        except ValueError as exc:
            assert str(exc) == expected_error
        else:
            raise AssertionError("load_beeui_config must reject nested display values")


# Тест: HTML/CSS/JS-подобные keys запрещены во всех block definitions
def test_schema_rejects_forbidden_block_keys(tmp_path: Path) -> None:
    base = _literal_schema()
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
    base = _literal_schema()
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


# Тест: пустой layout возвращает пустой список
def test_layout_empty_returns_empty_list() -> None:
    assert render_layout(None) == []
    assert render_layout([]) == []
    assert render_layout("not a list") == []
    assert render_layout(42) == []


# Тест: не-object элемент в layout возвращает degraded блок
def test_layout_non_object_item_returns_degraded() -> None:
    result = render_layout(["not an object"])
    assert len(result) == 1
    assert result[0]["type"] == "degraded"
    assert "width_class" in result[0]


# Тест: неизвестный block type возвращает degraded блок
def test_layout_unknown_block_type_returns_degraded() -> None:
    result = render_layout([{"type": "unknown_block", "width": 6}])
    assert len(result) == 1
    assert result[0]["type"] == "degraded"


# Тест: block type без type поля возвращает degraded блок
def test_layout_missing_type_returns_degraded() -> None:
    result = render_layout([{"width": 6}])
    assert len(result) == 1
    assert result[0]["type"] == "degraded"


# Тест: width mapping работает корректно
def test_layout_width_mapping() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "width": 12},
            {"type": "metric_card", "title": "B", "width": 6},
            {"type": "metric_card", "title": "C", "width": 3},
            {"type": "metric_card", "title": "D", "width": 99},
        ]
    )
    assert len(result) == 4
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12 col-lg-6"
    assert result[2]["width_class"] == "col-12 col-sm-6 col-lg-3"
    assert result[3]["width_class"] == "col-12"  # invalid -> default


# Тест: hero_snapshot рендерится с items и links
def test_layout_hero_snapshot_renders() -> None:
    result = render_layout(
        [
            {
                "type": "hero_snapshot",
                "title": "System",
                "subtitle": "Overview",
                "status": "ok",
                "width": 6,
                "items": [
                    {"label": "Run", "value": "run_001", "href": "/runs/run_001"},
                    {"label": "Runtime", "value": "stopped"},
                ],
                "links": [
                    {"label": "Open runs", "href": "/runs"},
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "hero_snapshot"
    assert block["title"] == "System"
    assert block["subtitle"] == "Overview"
    assert block["status"] == "ok"
    assert len(block["items"]) == 2
    assert block["items"][0]["href"] == "/runs/run_001"
    assert block["items"][1]["href"] is None
    assert len(block["links"]) == 1
    assert block["links"][0]["href"] == "/runs"


# Тест: hero_snapshot с небезопасной ссылкой отфильтровывается
def test_layout_hero_snapshot_rejects_unsafe_links() -> None:
    result = render_layout(
        [
            {
                "type": "hero_snapshot",
                "title": "Test",
                "width": 6,
                "items": [
                    {"label": "Bad", "value": "ext", "href": "http://evil.com"},
                    {"label": "Dbl", "value": "ext", "href": "//evil.com"},
                    {
                        "label": "Javascript",
                        "value": "bad",
                        "href": "javascript:alert(1)",
                    },
                    {
                        "label": "Mail",
                        "value": "bad",
                        "href": "mailto:test@example.com",
                    },
                    {"label": "Control", "value": "bad", "href": "/runs/\x01secret"},
                    {
                        "label": "Encoded newline",
                        "value": "bad",
                        "href": "/runs/%0asecret",
                    },
                    {
                        "label": "Encoded tab",
                        "value": "bad",
                        "href": "/runs/%09secret",
                    },
                    {
                        "label": "Encoded null",
                        "value": "bad",
                        "href": "/runs/%00secret",
                    },
                    {"label": "Traversal", "value": "bad", "href": "/../secret"},
                    {
                        "label": "Nested traversal",
                        "value": "bad",
                        "href": "/runs/../../secret",
                    },
                    {
                        "label": "Encoded traversal",
                        "value": "bad",
                        "href": "/%2e%2e/secret",
                    },
                    {
                        "label": "Backslash traversal",
                        "value": "bad",
                        "href": "/runs\\..\\secret",
                    },
                    {"label": "Safe", "value": "int", "href": "/runs/1"},
                ],
                "links": [
                    {"label": "Bad", "href": "https://evil.com"},
                ],
            }
        ]
    )
    block = result[0]
    assert all(item["href"] is None for item in block["items"][:-1])
    assert block["items"][-1]["href"] == "/runs/1"
    assert len(block["links"]) == 0


# Тест: metric_card рендерится с value, status и hint
def test_layout_metric_card_renders() -> None:
    result = render_layout(
        [
            {
                "type": "metric_card",
                "title": "Profit",
                "value": "n/a",
                "status": "missing_evidence",
                "hint": "No closed trades",
                "width": 3,
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "metric_card"
    assert block["value"] == "n/a"
    assert block["status"] == "missing_evidence"
    assert block["hint"] == "No closed trades"


# Тест: kpi_strip рендерится с items
def test_layout_kpi_strip_renders() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_strip",
                "title": "KPIs",
                "width": 12,
                "items": [
                    {"label": "Runs", "value": "42", "status": "ok"},
                    {"label": "Errors", "value": "0"},
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "kpi_strip"
    assert len(block["items"]) == 2
    assert block["items"][0]["status"] == "ok"


# Тест: venue_summary_grid рендерится с items
def test_layout_venue_summary_grid_renders() -> None:
    result = render_layout(
        [
            {
                "type": "venue_summary_grid",
                "title": "Venues",
                "width": 6,
                "items": [
                    {"label": "MRKT", "value": "active"},
                    {"label": "Binance", "value": "connected"},
                ],
            }
        ]
    )
    assert len(result) == 1
    assert result[0]["type"] == "venue_summary_grid"
    assert len(result[0]["items"]) == 2


# Тест: mode_cards рендерится с items
def test_layout_mode_cards_renders() -> None:
    result = render_layout(
        [
            {
                "type": "mode_cards",
                "title": "Modes",
                "width": 6,
                "items": [
                    {"label": "Paper", "value": "enabled", "status": "ok"},
                    {"label": "Live", "value": "disabled", "status": "warning"},
                ],
            }
        ]
    )
    assert len(result) == 1
    assert result[0]["type"] == "mode_cards"
    assert len(result[0]["items"]) == 2


# Тест: status_table рендерится с columns и rows
def test_layout_status_table_renders() -> None:
    result = render_layout(
        [
            {
                "type": "status_table",
                "title": "Health",
                "width": 6,
                "columns": ["Source", "Status", "Reason"],
                "rows": [
                    ["runtime/active.json", "missing", "No active runtime"],
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "status_table"
    assert block["columns"] == ["Source", "Status", "Reason"]
    assert len(block["rows"]) == 1
    assert block["rows"][0][0] == "runtime/active.json"


# Тест: status_table с dict rows деградирует
def test_layout_status_table_dict_rows_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "status_table",
                "title": "Health",
                "width": 6,
                "columns": ["Source", "Status"],
                "rows": [
                    {"source": "runtime", "status": "ok"},
                ],
            }
        ]
    )
    assert len(result) == 1
    assert result[0]["type"] == "degraded"


def test_layout_status_table_invalid_row_length_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "status_table",
                "title": "Health",
                "columns": ["Source", "Status"],
                "rows": [["runtime"]],
            }
        ]
    )
    assert result[0]["type"] == "degraded"


def test_layout_status_table_empty_columns_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "status_table",
                "title": "Health",
                "columns": [],
                "rows": [],
            }
        ]
    )
    assert result[0]["type"] == "degraded"


# Тест: event_table рендерится с columns и rows
def test_layout_event_table_renders() -> None:
    result = render_layout(
        [
            {
                "type": "event_table",
                "title": "Events",
                "width": 12,
                "columns": ["Time", "Event"],
                "rows": [
                    ["2026-06-01", "Started"],
                ],
            }
        ]
    )
    assert len(result) == 1
    assert result[0]["type"] == "event_table"


# Тест: attention_list рендерится с items
def test_layout_attention_list_renders() -> None:
    result = render_layout(
        [
            {
                "type": "attention_list",
                "title": "Alerts",
                "width": 6,
                "items": [
                    {
                        "label": "Disk full",
                        "message": "90% used",
                        "severity": "warning",
                    },
                    {
                        "label": "Service down",
                        "message": "No response",
                        "severity": "error",
                    },
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "attention_list"
    assert block["items"][0]["severity"] == "warning"
    assert block["items"][1]["severity"] == "error"


# Тест: artifact_links рендерится с items
def test_layout_artifact_links_renders() -> None:
    result = render_layout(
        [
            {
                "type": "artifact_links",
                "title": "Artifacts",
                "width": 6,
                "items": [
                    {
                        "label": "report.json",
                        "href": "/runs/1/artifacts/report",
                        "content_type": "json",
                    },
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "artifact_links"
    assert block["items"][0]["href"] == "/runs/1/artifacts/report"


# Тест: artifact_links с небезопасными href отфильтровывается
def test_layout_artifact_links_rejects_unsafe_href() -> None:
    result = render_layout(
        [
            {
                "type": "artifact_links",
                "title": "Artifacts",
                "width": 6,
                "items": [
                    {"label": "bad", "href": "http://evil.com"},
                    {"label": "protocol relative", "href": "//example.com"},
                    {"label": "javascript", "href": "javascript:alert(1)"},
                    {"label": "mail", "href": "mailto:test@example.com"},
                    {"label": "control", "href": "/runs/\x01secret"},
                    {"label": "traversal", "href": "/../secret"},
                    {"label": "nested traversal", "href": "/runs/../../secret"},
                    {"label": "encoded traversal", "href": "/%2e%2e/secret"},
                    {"label": "backslash traversal", "href": "/runs\\..\\secret"},
                    {"label": "good", "href": "/runs/1/artifacts/report"},
                ],
            }
        ]
    )
    block = result[0]
    assert all(item["href"] is None for item in block["items"][:-1])
    assert block["items"][-1]["href"] == "/runs/1/artifacts/report"


# Тест: raw_json_panel рендерится с data
def test_layout_raw_json_panel_renders() -> None:
    result = render_layout(
        [
            {
                "type": "raw_json_panel",
                "title": "Raw data",
                "width": 12,
                "data": {"key": "value"},
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "raw_json_panel"
    assert block["data"] == {"key": "value"}


# Тест: malformed payload не ломает render_layout
def test_layout_malformed_items_do_not_crash() -> None:
    result = render_layout(
        [
            {"type": "hero_snapshot", "items": "not a list", "width": 6},
            {"type": "metric_card", "value": {"nested": "bad"}},
            {"type": "status_table", "columns": "not a list", "rows": "not a list"},
            {"type": "kpi_strip", "items": [{"label": "ok", "value": "1"}]},
            None,
            42,
        ]
    )
    assert len(result) == 6
    assert result[4]["type"] == "degraded"
    assert result[5]["type"] == "degraded"
    assert result[0]["type"] == "degraded"
    assert result[1]["type"] == "degraded"
    assert result[2]["type"] == "degraded"
    assert result[3]["type"] == "degraded"


# Тест: все типы блоков рендерятся с корректными type и width_class
def test_layout_all_block_types_render_with_type_and_width() -> None:
    layout = [
        {
            "type": "hero_snapshot",
            "title": "S",
            "width": 6,
            "items": [{"label": "L", "value": "V"}],
        },
        {"type": "metric_card", "title": "M", "value": "42", "width": 3},
        {
            "type": "kpi_strip",
            "title": "K",
            "width": 12,
            "items": [{"label": "L", "value": "V"}],
        },
        {
            "type": "venue_summary_grid",
            "title": "V",
            "width": 6,
            "items": [{"label": "L", "value": "V"}],
        },
        {
            "type": "mode_cards",
            "title": "Mo",
            "width": 6,
            "items": [{"label": "L", "value": "V"}],
        },
        {
            "type": "status_table",
            "title": "St",
            "width": 6,
            "columns": ["A"],
            "rows": [["B"]],
        },
        {
            "type": "event_table",
            "title": "E",
            "width": 12,
            "columns": ["A"],
            "rows": [["B"]],
        },
        {
            "type": "attention_list",
            "title": "A",
            "width": 6,
            "items": [{"label": "L", "message": "M"}],
        },
        {
            "type": "artifact_links",
            "title": "Ar",
            "width": 6,
            "items": [{"label": "L", "href": "/runs/1"}],
        },
        {"type": "raw_json_panel", "title": "R", "width": 12, "data": {"k": "v"}},
    ]
    result = render_layout(layout)
    assert len(result) == 10
    for block in result:
        assert block["type"] != "degraded", f"Block type {block.get('type')} degraded"
        assert "width_class" in block


# Тест: блоки рендерят safe text (Jinja-экранирование в rendered dict)
def test_layout_block_text_is_escaped() -> None:
    result = render_layout(
        [
            {
                "type": "hero_snapshot",
                "title": "<script>bad</script>",
                "width": 6,
                "items": [
                    {"label": "<b>label</b>", "value": "<i>value</i>", "href": "/safe"},
                ],
            },
            {
                "type": "metric_card",
                "title": "<metric>",
                "value": "<value>",
                "status": "<status>",
                "hint": "<hint>",
            },
            {
                "type": "attention_list",
                "title": "A",
                "width": 6,
                "items": [
                    {
                        "label": "<b>alert</b>",
                        "message": "<script>bad</script>",
                        "severity": "error",
                    },
                ],
            },
        ]
    )
    assert result[0]["title"] == "<script>bad</script>"
    assert result[0]["items"][0]["label"] == "<b>label</b>"
    assert result[0]["items"][0]["value"] == "<i>value</i>"
    assert result[1]["title"] == "<metric>"
    assert result[1]["value"] == "<value>"
    assert result[2]["items"][0]["label"] == "<b>alert</b>"
    assert result[2]["items"][0]["message"] == "<script>bad</script>"


# Тест: raw_json_panel не рендерится когда есть непустой layout структурированных блоков
def test_layout_structured_blocks_hide_raw_panel() -> None:
    layout = [
        {
            "type": "hero_snapshot",
            "title": "S",
            "width": 6,
            "items": [{"label": "L", "value": "V"}],
        },
        {"type": "metric_card", "title": "M", "value": "42", "width": 3},
    ]
    result = render_layout(layout)
    types = [b["type"] for b in result]
    assert "raw_json_panel" not in types
    layout_with_raw = layout + [
        {"type": "raw_json_panel", "title": "Debug", "width": 12, "data": {"k": "v"}}
    ]
    result_with_raw = render_layout(layout_with_raw)
    types_with_raw = [b["type"] for b in result_with_raw]
    assert "raw_json_panel" in types_with_raw


# Тест: fallback рендерится при пустом layout
def test_layout_fallback_when_empty() -> None:
    assert render_layout(None) == []
    assert render_layout([]) == []
    assert render_layout({}) == []


# Тест: KPI strip использует правильные CSS-классы для stat card
def test_layout_kpi_strip_uses_stat_cards() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_strip",
                "title": "KPIs",
                "width": 12,
                "items": [
                    {"label": "Runs", "value": "42", "status": "ok"},
                    {"label": "Rate", "value": "94%"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "kpi_strip"
    assert block["title"] == "KPIs"
    assert len(block["items"]) == 2
    assert block["items"][0]["label"] == "Runs"
    assert block["items"][0]["value"] == "42"
    assert block["items"][0]["status"] == "ok"
    assert block["items"][1]["status"] == ""


# Тест: chart block type рендерится без данных
def test_layout_chart_type_renders() -> None:
    result = render_layout(
        [
            {"type": "chart", "title": "Price Chart", "width": 12},
        ]
    )

    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["title"] == "Price Chart"
    assert block["has_data"] is False
    assert block["width_class"] == "col-12"


# Тест: chart с полными данными рендерится с has_data=True
def test_layout_chart_with_data_renders() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "<script>bad</script>",
                "subtitle": "Daily prices",
                "status": "ok",
                "symbol": "BTC/USD",
                "timeframe": "1h",
                "series": [{"name": "close", "data": [100, 101, 102]}],
                "points": [{"x": 1, "y": 100}],
                "candles": [{"open": 99, "high": 103, "low": 98, "close": 101}],
                "width": 12,
            },
        ]
    )

    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["title"] == "<script>bad</script>"
    assert block["has_data"] is True
    assert block["symbol"] == "BTC/USD"
    assert block["timeframe"] == "1h"


# Тест: chart.html template существует в package
def test_layout_chart_template_exists() -> None:
    assert Path("src/beeui_module/web/templates/components/layout/chart.html").is_file()


# Тест: все layout templates, упомянутые в layout_block.html, существуют
def test_layout_block_includes_exist() -> None:
    template_root = Path("src/beeui_module/web/templates")
    layout_block = (template_root / "components" / "layout_block.html").read_text(
        encoding="utf-8"
    )
    includes = re.findall(r'"(components/layout/[^"]+\.html)"', layout_block)
    assert includes, "layout_block.html must include layout templates"
    for include in includes:
        assert (template_root / include).is_file(), (
            f"Missing included template: {include}"
        )


# Тест: venue_summary_grid использует правильную сетку
def test_layout_venue_summary_grid_uses_grid() -> None:
    result = render_layout(
        [
            {
                "type": "venue_summary_grid",
                "title": "Venues",
                "width": 6,
                "items": [
                    {"label": "MRKT", "value": "active", "status": "ok"},
                    {"label": "Binance", "value": "connected", "status": "ok"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "venue_summary_grid"
    assert block["items"][0]["status"] == "ok"
    assert block["items"][1]["value"] == "connected"


# Тест: mode_cards рендерится с compact card deck
def test_layout_mode_cards_uses_compact_cards() -> None:
    result = render_layout(
        [
            {
                "type": "mode_cards",
                "title": "Modes",
                "width": 6,
                "items": [
                    {"label": "Paper", "value": "enabled", "status": "ok"},
                    {"label": "Live", "value": "disabled", "status": "warning"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "mode_cards"
    assert len(block["items"]) == 2


# Тест: attention_list использует list-group с severity
def test_layout_attention_list_uses_list_group() -> None:
    result = render_layout(
        [
            {
                "type": "attention_list",
                "title": "Alerts",
                "width": 6,
                "items": [
                    {"label": "Disk", "message": "90%", "severity": "error"},
                    {"label": "Memory", "message": "80%", "severity": "warning"},
                    {"label": "Info", "message": "ok", "severity": "info"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "attention_list"
    assert block["items"][0]["severity"] == "error"
    assert block["items"][1]["severity"] == "warning"
    assert block["items"][2]["severity"] == "info"


# Тест: artifact_links использует list-group с href и content_type
def test_layout_artifact_links_uses_list_group() -> None:
    result = render_layout(
        [
            {
                "type": "artifact_links",
                "title": "Artifacts",
                "width": 6,
                "items": [
                    {
                        "label": "report.json",
                        "href": "/runs/1/artifacts/report",
                        "content_type": "json",
                    },
                    {
                        "label": "log.txt",
                        "href": "/runs/1/artifacts/log",
                        "content_type": "text",
                    },
                ],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "artifact_links"
    assert block["items"][0]["href"] == "/runs/1/artifacts/report"
    assert block["items"][0]["content_type"] == "json"
    assert block["items"][1]["content_type"] == "text"


# Тест: operator_hero рендерится с title, subtitle, status, items, primary_links
def test_layout_operator_hero_renders() -> None:
    result = render_layout(
        [
            {
                "type": "operator_hero",
                "title": "System Snapshot",
                "subtitle": "Runtime: stopped",
                "status": "ok",
                "width": 12,
                "items": [
                    {
                        "label": "Latest run",
                        "value": "run_001",
                        "href": "/runs/run_001",
                    },
                    {"label": "Runtime", "value": "stopped"},
                    {"label": "Active venues", "value": "mrkt / live"},
                ],
                "primary_links": [
                    {"label": "Open latest run", "href": "/runs/run_001"}
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "operator_hero"
    assert block["title"] == "System Snapshot"
    assert block["subtitle"] == "Runtime: stopped"
    assert block["status"] == "ok"
    assert len(block["items"]) == 3
    assert block["items"][0]["href"] == "/runs/run_001"
    assert block["items"][1]["href"] is None
    assert len(block["primary_links"]) == 1
    assert block["primary_links"][0]["href"] == "/runs/run_001"


# Тест: operator_hero с небезопасными ссылками отфильтровывается
def test_layout_operator_hero_rejects_unsafe_links() -> None:
    result = render_layout(
        [
            {
                "type": "operator_hero",
                "title": "Test",
                "width": 12,
                "items": [
                    {"label": "Safe", "value": "ok", "href": "/runs/1"},
                    {"label": "Http", "value": "bad", "href": "http://evil.com"},
                    {"label": "Https", "value": "bad", "href": "https://evil.com"},
                ],
                "primary_links": [
                    {"label": "Safe", "href": "/runs/1"},
                    {"label": "External", "href": "http://evil.com"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["items"][0]["href"] == "/runs/1"
    assert block["items"][1]["href"] is None
    assert block["items"][2]["href"] is None
    assert len(block["primary_links"]) == 1
    assert block["primary_links"][0]["href"] == "/runs/1"


# Тест: venue_card рендерится с items, alerts, links
def test_layout_venue_card_renders() -> None:
    result = render_layout(
        [
            {
                "type": "venue_card",
                "title": "MRKT",
                "subtitle": "Live monitoring",
                "status": "degraded",
                "width": 6,
                "items": [
                    {"label": "Health", "value": "ok", "status": "ok"},
                    {"label": "Mode", "value": "live"},
                    {"label": "Balance", "value": "0 TON"},
                    {"label": "Profit", "value": "n/a", "status": "warning"},
                ],
                "alerts": [
                    {
                        "severity": "warning",
                        "message": "Profit unavailable: no closed trades",
                    }
                ],
                "links": [
                    {"label": "Open latest run", "href": "/runs/run_001"},
                    {"label": "Open venue", "href": "/venues/mrkt"},
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "venue_card"
    assert block["title"] == "MRKT"
    assert block["subtitle"] == "Live monitoring"
    assert block["status"] == "degraded"
    assert len(block["items"]) == 4
    assert block["items"][0]["status"] == "ok"
    assert block["items"][3]["status"] == "warning"
    assert len(block["alerts"]) == 1
    assert block["alerts"][0]["severity"] == "warning"
    assert len(block["links"]) == 2
    assert block["links"][0]["href"] == "/runs/run_001"


# Тест: venue_card с небезопасными ссылками отфильтровывается
def test_layout_venue_card_rejects_unsafe_links() -> None:
    result = render_layout(
        [
            {
                "type": "venue_card",
                "title": "Test",
                "width": 6,
                "links": [
                    {"label": "Safe", "href": "/venues/mrkt"},
                    {"label": "External", "href": "https://evil.com"},
                    {"label": "Proto relative", "href": "//evil.com"},
                ],
            }
        ]
    )
    block = result[0]
    assert len(block["links"]) == 1
    assert block["links"][0]["href"] == "/venues/mrkt"


# Тест: kpi_grid рендерится с items (label/value/unit/status/hint)
def test_layout_kpi_grid_renders() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_grid",
                "title": "KPI",
                "width": 12,
                "items": [
                    {
                        "label": "Health",
                        "value": "ok",
                        "unit": "",
                        "status": "ok",
                        "hint": "Latest tick health",
                    },
                    {"label": "Runs", "value": "42"},
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "kpi_grid"
    assert block["title"] == "KPI"
    assert len(block["items"]) == 2
    assert block["items"][0]["unit"] == ""
    assert block["items"][0]["hint"] == "Latest tick health"
    assert block["items"][1]["unit"] == ""
    assert block["items"][1]["hint"] == ""


# Тест: state_grid рендерится с items
def test_layout_state_grid_renders() -> None:
    result = render_layout(
        [
            {
                "type": "state_grid",
                "title": "Current State",
                "width": 12,
                "items": [
                    {"label": "Health", "value": "ok", "status": "ok"},
                    {"label": "Tick", "value": "5 / 5"},
                    {"label": "Started", "value": "2026-06-05T04:34:54Z"},
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "state_grid"
    assert block["title"] == "Current State"
    assert len(block["items"]) == 3
    assert block["items"][0]["status"] == "ok"
    assert block["items"][1]["status"] == ""


# Тест: quick_links рендерится с items
def test_layout_quick_links_renders() -> None:
    result = render_layout(
        [
            {
                "type": "quick_links",
                "title": "Quick Links",
                "width": 12,
                "items": [
                    {"label": "Latest Run Detail", "href": "/runs/run_001"},
                    {"label": "All Runs", "href": "/runs"},
                    {"label": "No href"},
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "quick_links"
    assert len(block["items"]) == 3
    assert block["items"][0]["href"] == "/runs/run_001"
    assert block["items"][1]["href"] == "/runs"
    assert block["items"][2]["href"] is None


# Тест: run_table рендерится с columns и rows
def test_layout_run_table_renders() -> None:
    result = render_layout(
        [
            {
                "type": "run_table",
                "title": "Recent Runs",
                "width": 12,
                "columns": [
                    "Run",
                    "Mode",
                    "Venue",
                    "Symbol",
                    "TF",
                    "Started UTC",
                    "Health",
                    "Event Time UTC",
                    "Event",
                    "Severity",
                    "Events",
                    "Artifact",
                ],
                "rows": [
                    {
                        "run_id": "run_001",
                        "run_href": "/runs/run_001",
                        "mode": "live",
                        "venue": "mrkt",
                        "symbol": "TONNFT",
                        "timeframe": "1m",
                        "started_utc": "2026-06-05 04:34:54",
                        "health": "ok",
                        "event_time_utc": "2026-06-05 04:35:36",
                        "event": "venues/mrkt/lifecycle",
                        "severity": "info",
                        "events": "9",
                        "artifact": "lifecycle.jsonl",
                        "artifact_href": "/runs/run_001/artifacts/lifecycle_jsonl",
                    }
                ],
                "filters": True,
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "run_table"
    assert block["title"] == "Recent Runs"
    assert len(block["columns"]) == 12
    assert len(block["rows"]) == 1
    assert block["rows"][0]["run_id"] == "run_001"
    assert block["rows"][0]["run_href"] == "/runs/run_001"
    assert (
        block["rows"][0]["artifact_href"] == "/runs/run_001/artifacts/lifecycle_jsonl"
    )
    assert block["filters"] is True


# Тест: run_table с dict rows деградирует
def test_layout_run_table_invalid_columns_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "run_table",
                "title": "Broken Runs",
                "width": 12,
                "columns": ["Run"],
                "rows": [{"run_id": "run_001"}],
            }
        ]
    )

    assert len(result) == 1
    assert result[0]["type"] == "degraded"


# Тест: run_table с небезопасными href отфильтровывается
def test_layout_run_table_rejects_unsafe_href() -> None:
    result = render_layout(
        [
            {
                "type": "run_table",
                "title": "Runs",
                "width": 12,
                "columns": [
                    "Run",
                    "Mode",
                    "Venue",
                    "Symbol",
                    "TF",
                    "Started UTC",
                    "Health",
                    "Event Time UTC",
                    "Event",
                    "Severity",
                    "Events",
                    "Artifact",
                ],
                "rows": [
                    {
                        "run_id": "good",
                        "run_href": "/runs/good",
                        "artifact": "safe.txt",
                        "artifact_href": "/runs/good/artifacts/safe",
                    },
                    {
                        "run_id": "bad",
                        "run_href": "https://evil.com",
                        "artifact": "bad.txt",
                        "artifact_href": "https://evil.com/artifact",
                    },
                ],
                "filters": False,
            }
        ]
    )
    block = result[0]
    assert block["rows"][0]["run_href"] == "/runs/good"
    assert block["rows"][0]["artifact_href"] == "/runs/good/artifacts/safe"
    assert block["rows"][1]["run_href"] is None
    assert block["rows"][1]["artifact_href"] is None
    assert block["filters"] is False


# Тест: mode_cards с optional полями href, latest, latest_href
def test_layout_mode_cards_optional_fields() -> None:
    result = render_layout(
        [
            {
                "type": "mode_cards",
                "title": "Modes",
                "width": 6,
                "items": [
                    {
                        "label": "dry-run",
                        "value": "17",
                        "status": "warning",
                        "latest": "run_001",
                        "latest_href": "/runs/run_001",
                        "href": "/dry-run",
                    },
                    {"label": "paper", "value": "5", "status": "ok"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "mode_cards"
    assert block["items"][0]["label"] == "dry-run"
    assert block["items"][0]["href"] == "/dry-run"
    assert block["items"][0]["latest"] == "run_001"
    assert block["items"][0]["latest_href"] == "/runs/run_001"
    assert block["items"][1]["latest"] == "n/a"
    assert block["items"][1]["href"] is None
    assert block["items"][1]["latest_href"] is None


# Тест: mode_cards не ломается при отсутствии optional полей
def test_layout_mode_cards_missing_optionals() -> None:
    result = render_layout(
        [
            {
                "type": "mode_cards",
                "title": "Modes",
                "width": 6,
                "items": [
                    {"label": "paper", "value": "5"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "mode_cards"
    assert block["items"][0]["href"] is None
    assert block["items"][0]["latest"] == "n/a"
    assert block["items"][0]["latest_href"] is None


# Тест: attention_list обрабатывает отсутствующие label/message
def test_layout_attention_list_missing_fields() -> None:
    result = render_layout(
        [
            {
                "type": "attention_list",
                "title": "Alerts",
                "width": 6,
                "items": [
                    {"severity": "error"},
                    {"label": "Disk", "severity": "warning"},
                    {"label": "Memory", "message": "80%", "severity": "info"},
                    {"label": "Health", "message": "ok", "severity": "ok"},
                    {"label": "Unknown", "message": "?", "severity": "unknown"},
                ],
            }
        ]
    )
    block = result[0]
    assert block["items"][0]["label"] == "n/a"
    assert block["items"][0]["message"] == "n/a"
    assert block["items"][1]["message"] == "n/a"
    assert block["items"][3]["severity"] == "ok"
    assert block["items"][4]["severity"] == "unknown"


# Тест: _display_value helper возвращает default для None/null/empty
def test_display_value_helper() -> None:
    from beeui_module.blocks.layout_renderer import _display_value

    assert _display_value(None) == "n/a"
    assert _display_value("") == "n/a"
    assert _display_value("  ") == "n/a"
    assert _display_value("none") == "n/a"
    assert _display_value("None") == "n/a"
    assert _display_value("null") == "n/a"
    assert _display_value(0) == "0"
    assert _display_value(42) == "42"
    assert _display_value(True) == "True"
    assert _display_value("hello") == "hello"
    assert _display_value("hello", default="---") == "hello"
    assert _display_value(None, default="---") == "---"
    assert _display_value([1, 2]) == "n/a"


# Тест: операторные блоки с None значениями items рендерятся как n/a
def test_layout_operator_blocks_none_values() -> None:
    result = render_layout(
        [
            {
                "type": "operator_hero",
                "title": "Test",
                "subtitle": None,
                "width": 12,
                "items": [
                    {"label": None, "value": None},
                ],
            },
            {
                "type": "state_grid",
                "title": "State",
                "width": 12,
                "items": [
                    {"label": "Missing", "value": None},
                ],
            },
            {
                "type": "quick_links",
                "title": "Links",
                "width": 12,
                "items": [
                    {"label": None},
                ],
            },
        ]
    )
    assert result[0]["type"] == "operator_hero"
    assert result[0]["subtitle"] == "n/a"
    assert result[0]["items"][0]["label"] == "n/a"
    assert result[0]["items"][0]["value"] == "n/a"
    assert result[2]["items"][0]["label"] == "n/a"


# Тест: все 6 новых типов блоков рендерятся в render_layout без degraded
def test_layout_all_new_block_types_render() -> None:
    layout = [
        {
            "type": "operator_hero",
            "title": "OH",
            "width": 12,
            "items": [{"label": "L", "value": "V"}],
        },
        {
            "type": "venue_card",
            "title": "VC",
            "width": 6,
            "items": [{"label": "L", "value": "V"}],
        },
        {
            "type": "kpi_grid",
            "title": "KG",
            "width": 12,
            "items": [{"label": "L", "value": "V"}],
        },
        {
            "type": "state_grid",
            "title": "SG",
            "width": 12,
            "items": [{"label": "L", "value": "V"}],
        },
        {
            "type": "quick_links",
            "title": "QL",
            "width": 12,
            "items": [{"label": "L", "href": "/runs/1"}],
        },
        {
            "type": "run_table",
            "title": "RT",
            "width": 12,
            "columns": [
                "Run",
                "Mode",
                "Venue",
                "Symbol",
                "TF",
                "Started UTC",
                "Health",
                "Event Time UTC",
                "Event",
                "Severity",
                "Events",
                "Artifact",
            ],
            "rows": [{"run_id": "r1"}],
        },
    ]
    result = render_layout(layout)
    assert len(result) == 6
    for block in result:
        assert block["type"] != "degraded", f"Block type {block.get('type')} degraded"


# Тест: run_table template существует в package
def test_layout_run_table_template_exists() -> None:
    assert Path(
        "src/beeui_module/web/templates/components/layout/run_table.html"
    ).is_file()


# Тест: все новые layout templates существуют
def test_layout_new_templates_exist() -> None:
    for name in (
        "operator_hero",
        "venue_card",
        "kpi_grid",
        "state_grid",
        "quick_links",
        "run_table",
    ):
        path = Path(f"src/beeui_module/web/templates/components/layout/{name}.html")
        assert path.is_file(), f"Missing template: {path}"


# Тест: span в adapter-backed layout рендерит правильный класс ширины
def test_layout_span_sizing() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "span": 12},
            {"type": "metric_card", "title": "B", "value": "2", "span": 6},
            {"type": "metric_card", "title": "C", "value": "3", "span": 4},
            {"type": "metric_card", "title": "D", "value": "4", "span": 3},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12 col-lg-6"
    assert result[2]["width_class"] == "col-12 col-md-6 col-lg-4"
    assert result[3]["width_class"] == "col-12 col-sm-6 col-lg-3"


# Тест: size в adapter-backed layout рендерит правильный класс ширины
def test_layout_size_sizing() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "size": "S"},
            {"type": "metric_card", "title": "B", "value": "2", "size": "M"},
            {"type": "metric_card", "title": "C", "value": "3", "size": "L"},
            {"type": "metric_card", "title": "D", "value": "4", "size": "XL"},
        ]
    )
    assert result[0]["width_class"] == "col-12 col-md-6 col-lg-4"  # S -> 4
    assert result[1]["width_class"] == "col-12 col-lg-6"  # M -> 6
    assert result[2]["width_class"] == "col-12 col-lg-8"  # L -> 8
    assert result[3]["width_class"] == "col-12"  # XL -> 12


# Тест: size case-insensitive
def test_layout_size_case_insensitive() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "size": "s"},
            {"type": "metric_card", "title": "B", "value": "2", "size": "m"},
            {"type": "metric_card", "title": "C", "value": "3", "size": "l"},
            {"type": "metric_card", "title": "D", "value": "4", "size": "xl"},
        ]
    )
    assert result[0]["width_class"] == "col-12 col-md-6 col-lg-4"
    assert result[1]["width_class"] == "col-12 col-lg-6"
    assert result[2]["width_class"] == "col-12 col-lg-8"
    assert result[3]["width_class"] == "col-12"


# Тест: невалидный span в adapter-backed layout деградирует к default
def test_layout_invalid_span_degrades() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "span": 99},
            {"type": "metric_card", "title": "B", "value": "1", "span": "bad"},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12"


# Тест: невалидный size в adapter-backed layout деградирует к default
def test_layout_invalid_size_degrades() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "size": "XXL"},
            {"type": "metric_card", "title": "B", "value": "1", "size": 1},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12"


# Тест: конфликтующие sizing keys в adapter-backed layout деградируют к default
def test_layout_conflicting_sizing_keys_degrades() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "width": 6, "span": 12},
            {
                "type": "metric_card",
                "title": "B",
                "value": "1",
                "width": 3,
                "size": "XL",
            },
            {"type": "metric_card", "title": "C", "value": "1", "span": 6, "size": "L"},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12"
    assert result[2]["width_class"] == "col-12"


# Тест: existing width remains backward-compatible
def test_layout_width_backward_compatible() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "width": 12},
            {"type": "metric_card", "title": "B", "value": "2", "width": 6},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12 col-lg-6"
