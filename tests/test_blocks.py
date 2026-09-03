from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from beeui_module.blocks.layout_renderer import render_layout, resolve_layout_links
from beeui_module.pages.config import load_beeui_config
from beeui_module.pages.links import validate_internal_href


def _write_schema(tmp_path: Path, content: str) -> Path:
    schema_path = tmp_path / "schema.yml"
    schema_path.write_text(content, encoding="utf-8")
    return schema_path


def _base_schema() -> str:
    return Path("config/schema.yml").read_text(encoding="utf-8")


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


def test_schema_rejects_invalid_block_id(tmp_path: Path) -> None:
    base = _base_schema()
    invalid = base.replace("  latest_run:", "  Latest Run:", 1)

    try:
        load_beeui_config(_write_schema(tmp_path, invalid))
    except ValueError as exc:
        assert str(exc) == "blocks.Latest Run must be a safe identifier"
    else:
        raise AssertionError("load_beeui_config must reject unsafe block id")


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


def test_layout_empty_returns_empty_list() -> None:
    assert render_layout(None) == []
    assert render_layout([]) == []
    assert render_layout("not a list") == []
    assert render_layout(42) == []


def test_layout_non_object_item_returns_degraded() -> None:
    result = render_layout(["not an object"])
    assert len(result) == 1
    assert result[0]["type"] == "degraded"
    assert "width_class" in result[0]


def test_layout_unknown_block_type_returns_degraded() -> None:
    result = render_layout([{"type": "unknown_block", "width": 6}])
    assert len(result) == 1
    assert result[0]["type"] == "degraded"


def test_layout_missing_type_returns_degraded() -> None:
    result = render_layout([{"width": 6}])
    assert len(result) == 1
    assert result[0]["type"] == "degraded"


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


def test_layout_fallback_when_empty() -> None:
    assert render_layout(None) == []
    assert render_layout([]) == []
    assert render_layout({}) == []


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
    assert block["kind"] == "line"
    assert block["series"] == [{"name": "close", "data": [100, 101, 102]}]


def test_layout_chart_template_exists_for_chart_block() -> None:
    assert Path("src/beeui_module/web/templates/components/layout/chart.html").is_file()


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


def test_layout_run_table_template_exists() -> None:
    assert Path(
        "src/beeui_module/web/templates/components/layout/run_table.html"
    ).is_file()


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


def test_layout_invalid_span_degrades() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "span": 99},
            {"type": "metric_card", "title": "B", "value": "1", "span": "bad"},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12"


def test_layout_invalid_size_degrades() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "size": "XXL"},
            {"type": "metric_card", "title": "B", "value": "1", "size": 1},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12"


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


def test_layout_width_backward_compatible() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "width": 12},
            {"type": "metric_card", "title": "B", "value": "2", "width": 6},
        ]
    )
    assert result[0]["width_class"] == "col-12"
    assert result[1]["width_class"] == "col-12 col-lg-6"


def test_layout_span_supported() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "span": 6},
        ]
    )
    assert result[0]["width_class"] == "col-12 col-lg-6"


def test_layout_size_supported() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "size": "M"},
        ]
    )
    assert result[0]["width_class"] == "col-12 col-lg-6"


def test_layout_size_s() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "size": "S"},
        ]
    )
    assert result[0]["width_class"] == "col-12 col-md-6 col-lg-4"


def test_layout_malformed_sizing_degrades() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "width": "bogus"},
            {"type": "metric_card", "title": "B", "value": "2", "span": "bogus"},
            {"type": "metric_card", "title": "C", "value": "3", "size": "bogus"},
            {"type": "metric_card", "title": "D", "value": "4", "width": -1},
            {"type": "metric_card", "title": "E", "value": "5", "width": 99},
        ]
    )
    for block in result:
        assert block["width_class"] == "col-12", (
            f"Expected col-12 for malformed sizing, got {block['width_class']}"
        )


def test_layout_conflicting_sizing_degrades() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "width": 6, "span": 8},
            {"type": "metric_card", "title": "B", "value": "2", "span": 6, "size": "L"},
        ]
    )
    for block in result:
        assert block["width_class"] == "col-12", (
            f"Expected col-12 for conflicting sizing, got {block['width_class']}"
        )


def test_layout_kpi_grid_columns_1() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_grid",
                "title": "KPI",
                "columns": 1,
                "items": [{"label": "A", "value": "1"}, {"label": "B", "value": "2"}],
            }
        ]
    )
    assert result[0]["columns"] == 1
    assert result[0]["column_classes"] == "col-12"


def test_layout_kpi_grid_columns_2() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_grid",
                "title": "KPI",
                "columns": 2,
                "items": [{"label": "A", "value": "1"}, {"label": "B", "value": "2"}],
            }
        ]
    )
    assert result[0]["columns"] == 2
    assert result[0]["column_classes"] == "col-12 col-sm-6"


def test_layout_kpi_grid_columns_3() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_grid",
                "title": "KPI",
                "columns": 3,
                "items": [{"label": "A", "value": "1"}],
            }
        ]
    )
    assert result[0]["columns"] == 3
    assert result[0]["column_classes"] == "col-12 col-sm-6 col-lg-4"


def test_layout_kpi_grid_columns_4() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_grid",
                "title": "KPI",
                "columns": 4,
                "items": [{"label": "A", "value": "1"}],
            }
        ]
    )
    assert result[0]["columns"] == 4
    assert result[0]["column_classes"] == "col-12 col-sm-6 col-lg-3"


def test_layout_kpi_grid_columns_default() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_grid",
                "title": "KPI",
                "items": [{"label": "A", "value": "1"}],
            }
        ]
    )
    assert result[0]["columns"] == 4
    assert result[0]["column_classes"] == "col-12 col-sm-6 col-lg-3"


def test_layout_kpi_grid_invalid_columns_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "kpi_grid",
                "title": "KPI",
                "columns": 99,
                "items": [{"label": "A", "value": "1"}],
            },
            {
                "type": "kpi_grid",
                "title": "KPI2",
                "columns": "bad",
                "items": [{"label": "B", "value": "2"}],
            },
            {
                "type": "kpi_grid",
                "title": "KPI3",
                "columns": 0,
                "items": [{"label": "C", "value": "3"}],
            },
        ]
    )
    for block in result:
        assert block["columns"] == 4, f"Expected default 4, got {block['columns']}"
        assert block["column_classes"] == "col-12 col-sm-6 col-lg-3"


def test_layout_group_renders() -> None:
    result = render_layout(
        [
            {
                "type": "group",
                "width": 6,
                "direction": "vertical",
                "children": [
                    {
                        "type": "metric_card",
                        "title": "Storage",
                        "value": "42",
                        "width": 12,
                    },
                    {
                        "type": "metric_card",
                        "title": "Activity",
                        "value": "active",
                        "width": 12,
                    },
                ],
            }
        ]
    )
    assert len(result) == 1
    group = result[0]
    assert group["type"] == "group"
    assert group["width_class"] == "col-12 col-lg-6"
    assert group["direction"] == "vertical"
    assert len(group["children"]) == 2
    assert group["children"][0]["type"] == "metric_card"
    assert group["children"][0]["title"] == "Storage"
    assert group["children"][1]["title"] == "Activity"


def test_layout_group_and_block_as_columns() -> None:
    result = render_layout(
        [
            {
                "type": "group",
                "width": 6,
                "direction": "vertical",
                "children": [
                    {
                        "type": "metric_card",
                        "title": "Storage",
                        "value": "42",
                        "width": 12,
                    },
                ],
            },
            {
                "type": "metric_card",
                "title": "Dev Activity",
                "value": "active",
                "width": 6,
            },
        ]
    )
    assert len(result) == 2
    assert result[0]["type"] == "group"
    assert result[0]["width_class"] == "col-12 col-lg-6"
    assert result[1]["type"] == "metric_card"
    assert result[1]["width_class"] == "col-12 col-lg-6"


def test_layout_group_children_width_12() -> None:
    result = render_layout(
        [
            {
                "type": "group",
                "width": 12,
                "children": [
                    {
                        "type": "metric_card",
                        "title": "Full",
                        "value": "1",
                        "width": 12,
                    },
                ],
            }
        ]
    )
    group = result[0]
    assert group["children"][0]["width_class"] == "col-12"


def test_layout_group_malformed_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "group",
                "width": 6,
                "children": "not a list",
            },
            {
                "type": "group",
                "width": 6,
                "children": [{"type": "metric_card", "title": "A", "value": "1"}],
            },
        ]
    )

    assert len(result) == 2
    assert result[0]["type"] == "degraded"
    assert result[0]["width_class"] == "col-12 col-lg-6"
    assert "children" in result[0]["reason"]

    assert result[1]["type"] == "group"
    assert len(result[1]["children"]) == 1


def test_layout_group_missing_direction_defaults() -> None:
    result = render_layout(
        [
            {
                "type": "group",
                "width": 6,
                "children": [
                    {"type": "metric_card", "title": "A", "value": "1"},
                ],
            }
        ]
    )
    assert result[0]["direction"] == "vertical"


def test_layout_group_invalid_direction_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "group",
                "width": 6,
                "direction": "horizontal",
                "children": [
                    {"type": "metric_card", "title": "A", "value": "1"},
                ],
            }
        ]
    )
    assert result[0]["direction"] == "vertical"


def test_layout_group_depth_bounded() -> None:
    result = render_layout(
        [
            {
                "type": "group",
                "width": 12,
                "children": [
                    {
                        "type": "group",
                        "width": 12,
                        "children": [
                            {
                                "type": "group",
                                "width": 12,
                                "children": [
                                    {
                                        "type": "group",
                                        "width": 12,
                                        "children": [
                                            {
                                                "type": "metric_card",
                                                "title": "Too deep",
                                                "value": "1",
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    )
    inner = result[0]["children"][0]["children"][0]["children"][0]
    assert inner["type"] == "degraded"
    assert "depth exceeded" in inner["reason"]


def test_layout_flat_6_3_3() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "width": 6},
            {"type": "metric_card", "title": "B", "value": "2", "width": 3},
            {"type": "metric_card", "title": "C", "value": "3", "width": 3},
        ]
    )
    assert result[0]["width_class"] == "col-12 col-lg-6"
    assert result[1]["width_class"] == "col-12 col-sm-6 col-lg-3"
    assert result[2]["width_class"] == "col-12 col-sm-6 col-lg-3"


def test_layout_flat_3_3_3_3() -> None:
    result = render_layout(
        [
            {"type": "metric_card", "title": "A", "value": "1", "width": 3},
            {"type": "metric_card", "title": "B", "value": "2", "width": 3},
            {"type": "metric_card", "title": "C", "value": "3", "width": 3},
            {"type": "metric_card", "title": "D", "value": "4", "width": 3},
        ]
    )
    for block in result:
        assert block["width_class"] == "col-12 col-sm-6 col-lg-3"


def test_layout_group_template_exists() -> None:
    assert Path("src/beeui_module/web/templates/components/layout/group.html").is_file()


def test_resolve_kpi_grid_columns() -> None:
    from beeui_module.blocks.layout_renderer import resolve_kpi_grid_columns

    assert resolve_kpi_grid_columns(1) == 1
    assert resolve_kpi_grid_columns(2) == 2
    assert resolve_kpi_grid_columns(3) == 3
    assert resolve_kpi_grid_columns(4) == 4
    assert resolve_kpi_grid_columns(99) == 4
    assert resolve_kpi_grid_columns(0) == 4
    assert resolve_kpi_grid_columns("bad") == 4
    assert resolve_kpi_grid_columns(None) == 4
    assert resolve_kpi_grid_columns("3") == 4
    assert resolve_kpi_grid_columns(True) == 4
    assert resolve_kpi_grid_columns(False) == 4
    assert resolve_kpi_grid_columns(1.0) == 4


def test_layout_chart_line_renders() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Line Chart",
                "kind": "line",
                "width": 12,
                "series": [{"name": "close", "data": [1, 2, 3]}],
                "categories": ["A", "B", "C"],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["kind"] == "line"
    assert block["has_data"] is True


def test_layout_chart_bar_renders() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Bar Chart",
                "kind": "bar",
                "width": 6,
                "series": [{"name": "count", "data": [5, 10, 15]}],
                "categories": ["X", "Y", "Z"],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["kind"] == "bar"
    assert block["has_data"] is True


def test_layout_chart_area_renders() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Area Chart",
                "kind": "area",
                "width": 12,
                "series": [{"name": "volume", "data": [100, 200, 150]}],
                "categories": ["Jan", "Feb", "Mar"],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["kind"] == "area"
    assert block["has_data"] is True


def test_layout_chart_donut_renders() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Donut Chart",
                "kind": "donut",
                "width": 6,
                "series": [30, 50, 20],
                "labels": ["A", "B", "C"],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["kind"] == "donut"
    assert block["has_data"] is True


def test_layout_chart_unsupported_kind_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Bad Kind",
                "kind": "radar",
                "width": 12,
                "series": [{"name": "x", "data": [1, 2]}],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["kind"] == "line"
    assert block["state"] == "degraded"
    assert block["has_data"] is False


def test_layout_chart_empty_data_renders_empty() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Empty Chart",
                "kind": "line",
                "width": 12,
                "series": [],
                "categories": [],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["has_data"] is False


def test_layout_chart_invalid_series_degrades() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Invalid",
                "kind": "line",
                "width": 12,
                "series": "not a list",
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "chart"
    assert block["has_data"] is False
    assert block["state"] == "degraded"


def test_layout_chart_colors_accept_tokens_and_strict_hex_only() -> None:
    block = render_layout(
        [
            {
                "type": "chart",
                "title": "Colors",
                "kind": "line",
                "series": [{"name": "series", "data": [1]}],
                "colors": [
                    "primary",
                    "#6366f1",
                    "#0ea5e9",
                    "#10b981",
                    "#f59e0b",
                    "#ef4444",
                    "rgb(1,2,3)",
                    "#fff",
                    "#6366f180",
                    "url(https://invalid.example)",
                ],
            }
        ]
    )[0]
    assert block["chart_config"]["colors"] == [
        "var(--tblr-primary)",
        "#6366f1",
        "#0ea5e9",
        "#10b981",
        "#f59e0b",
        "#ef4444",
    ]


def test_layout_chart_series_requires_finite_numeric_data() -> None:
    invalid_values = [
        float("nan"),
        float("inf"),
        float("-inf"),
        True,
        "1",
        {"x": 1},
        [1],
    ]
    for value in invalid_values:
        block = render_layout(
            [
                {
                    "type": "chart",
                    "title": "Invalid",
                    "kind": "line",
                    "series": [{"name": "series", "data": [value]}],
                }
            ]
        )[0]
        assert block["state"] == "degraded"
        assert block["chart_config"]["series"] == []


def test_layout_chart_valid_series_and_empty_state_are_distinct() -> None:
    payloads = [
        ("line", [{"name": "line", "data": [1, 2.5]}]),
        ("bar", [{"name": "bar", "data": [1, 2]}]),
        ("area", [{"name": "area", "data": [1, 2]}]),
        ("donut", [1, 2.5]),
    ]
    for kind, series in payloads:
        block = render_layout(
            [{"type": "chart", "title": kind, "kind": kind, "series": series}]
        )[0]
        assert block["state"] == "ready"
        assert block["has_data"] is True

    empty = render_layout(
        [{"type": "chart", "title": "Empty", "kind": "line", "series": []}]
    )[0]
    assert empty["state"] == "empty"
    assert empty["chart_config"]["series"] == []


def test_layout_chart_unsafe_text_escaped() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "<script>bad</script>",
                "subtitle": "<b>sub</b>",
                "status": "<i>status</i>",
                "kind": "line",
                "width": 12,
                "series": [{"name": "<script>alert(1)</script>", "data": [1]}],
            }
        ]
    )
    block = result[0]
    assert block["title"] == "<script>bad</script>"
    assert block["subtitle"] == "<b>sub</b>"
    assert block["status"] == "<i>status</i>"


def test_layout_chart_safe_json_serialization() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Safe JSON",
                "kind": "line",
                "width": 12,
                "series": [{"name": "test", "data": [1, 2, 3]}],
                "categories": ["A", "B", "C"],
            }
        ]
    )
    block = result[0]
    assert "_chart_config" not in block
    assert isinstance(block["chart_config"], dict)

    config = block["chart_config"]
    assert config["chart"]["type"] == "line"
    assert config["series"][0]["name"] == "test"
    assert config["xaxis"]["categories"] == ["A", "B", "C"]
    assert config["chart"]["toolbar"]["show"] is False


def test_layout_chart_no_arbitrary_options() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "No arbitrary",
                "kind": "line",
                "width": 12,
                "series": [{"name": "x", "data": [1]}],
                "theme": {"palette": "custom"},
                "annotations": {"points": [{"x": 1}]},
            }
        ]
    )
    block = result[0]

    config = block["chart_config"]
    assert "annotations" not in config


def test_layout_chart_height_bounds() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Height",
                "kind": "line",
                "width": 12,
                "height": 999,
                "series": [{"name": "x", "data": [1]}],
            }
        ]
    )
    assert result[0]["height"] == 300

    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Height2",
                "kind": "line",
                "width": 12,
                "height": 200,
                "series": [{"name": "x", "data": [1]}],
            }
        ]
    )
    assert result[0]["height"] == 200


def test_layout_chart_deterministic_id() -> None:
    layout = [
        {
            "type": "chart",
            "title": "ID test",
            "kind": "line",
            "width": 12,
            "series": [{"name": "x", "data": [1]}],
        }
    ]

    first = render_layout(layout)
    second = render_layout(layout)

    assert first[0]["chart_id"].startswith("beeui-chart-")
    assert first[0]["chart_id"] == second[0]["chart_id"]


def test_layout_has_charts_detects_nested_group_chart() -> None:
    from beeui_module.blocks.layout_renderer import layout_has_charts

    blocks = render_layout(
        [
            {
                "type": "group",
                "children": [
                    {
                        "type": "chart",
                        "title": "Nested chart",
                        "series": [{"name": "x", "data": [1, 2, 3]}],
                    }
                ],
            }
        ]
    )

    assert layout_has_charts(blocks) is True


def test_layout_chart_template_exists() -> None:
    assert Path("src/beeui_module/web/templates/components/layout/chart.html").is_file()


def test_layout_data_table_basic_renders() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Recent Items",
                "width": 12,
                "variant": "card",
                "columns": [
                    {"key": "id", "label": "ID"},
                    {"key": "name", "label": "Name"},
                ],
                "rows": [
                    {"id": {"label": "001"}, "name": {"label": "Alice"}},
                    {"id": {"label": "002"}, "name": {"label": "Bob"}},
                ],
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "data_table"
    assert block["title"] == "Recent Items"
    assert len(block["columns"]) == 2
    assert len(block["rows"]) == 2
    assert block["rows"][0]["id"]["value"] == "001"


def test_layout_data_table_striped_renders() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Striped",
                "width": 12,
                "striped": True,
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["striped"] is True


def test_layout_data_table_mobile_renders() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Mobile",
                "width": 12,
                "mobile": "md",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["mobile"] == "md"


def test_layout_data_table_selectable_renders() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Selectable",
                "width": 12,
                "selectable": True,
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["selectable"] is True


def test_layout_data_table_compact_renders() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Compact",
                "width": 12,
                "compact": True,
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["compact"] is True


def test_layout_data_table_toolbar_renders() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar",
                "width": 12,
                "toolbar": {
                    "search": True,
                    "entries": True,
                    "actions": [{"label": "Export", "href": "/export"}],
                },
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    block = result[0]
    assert block["toolbar"]["search"] is True
    assert block["toolbar"]["entries"] is True
    assert len(block["toolbar"]["actions"]) == 1
    assert block["toolbar"]["actions"][0]["href"] == "/export"


def test_layout_data_table_toolbar_unsafe_link_rejected() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar",
                "width": 12,
                "toolbar": {
                    "actions": [
                        {"label": "External", "href": "https://evil.com"},
                        {"label": "Safe", "href": "/safe"},
                    ]
                },
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert len(result[0]["toolbar"]["actions"]) == 1
    assert result[0]["toolbar"]["actions"][0]["href"] == "/safe"


def test_layout_data_table_pagination_renders() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Paginated",
                "width": 12,
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "pagination": {
                    "label": "Showing 1 to 1 of 1 entries",
                    "pages": [
                        {"label": "1", "href": "/runs?page=1", "active": True},
                    ],
                },
            }
        ]
    )
    block = result[0]
    assert block["pagination"]["label"] == "Showing 1 to 1 of 1 entries"
    assert len(block["pagination"]["pages"]) == 1
    assert block["pagination"]["pages"][0]["active"] is True


def test_layout_data_table_pagination_unsafe_link_rejected() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Paginated",
                "width": 12,
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "pagination": {
                    "pages": [
                        {"label": "Bad", "href": "https://evil.com"},
                        {"label": "Good", "href": "/runs?page=2"},
                    ]
                },
            }
        ]
    )
    assert len(result[0]["pagination"]["pages"]) == 1
    assert result[0]["pagination"]["pages"][0]["label"] == "Good"


def test_data_table_live_identity_page_size_and_compact_pagination_normalize() -> None:
    pages = [
        {"label": str(number), "href": f"/queue?page={number}", "active": number == 67}
        for number in range(1, 135)
    ]
    result = render_layout(
        [
            {
                "type": "data_table",
                "id": "queue-table",
                "title": "Queue",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "pagination": {
                    "label": "Showing 1 to 25",
                    "pages": pages,
                    "page_size": {
                        "current": "25",
                        "options": [
                            {"value": "10", "label": "10", "href": "/queue?size=10"},
                            {
                                "value": "25",
                                "label": "25",
                                "href": "/queue?size=25",
                                "active": True,
                            },
                        ],
                    },
                },
            }
        ]
    )

    block = result[0]
    assert block["table_id"] == "queue-table"
    assert [page.get("label") for page in block["pagination"]["pages"]] == [
        "1",
        None,
        "66",
        "67",
        "68",
        None,
        "134",
    ]
    assert block["pagination"]["previous"]["href"] == "/queue?page=66"
    assert block["pagination"]["next"]["href"] == "/queue?page=68"
    assert block["pagination"]["page_size"]["current"] == "25"
    assert block["pagination"]["page_size"]["options"][0]["href"] == "/queue?size=10"


def test_data_table_live_metadata_and_page_size_degrade_safely() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "id": "unsafe selector[]",
                "title": "Queue",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "pagination": {
                    "page_param": "page[]",
                    "page_size": {
                        "options": [
                            {"label": "Unsafe", "href": "https://evil.example/size"},
                            {"label": "Safe", "href": "/queue?size=25"},
                        ]
                    },
                },
            }
        ]
    )

    assert result[0]["table_id"] is None
    assert result[0]["pagination"]["page_param"] == "page"
    assert result[0]["pagination"]["page_size"]["options"] == [
        {"value": "Safe", "label": "Safe", "href": "/queue?size=25", "active": False}
    ]


def test_data_table_compact_pagination_handles_empty_small_and_edges() -> None:
    def page(number: int, active: bool = False) -> dict[str, object]:
        return {"label": str(number), "href": f"/queue?page={number}", "active": active}

    def pagination_for(pages: list[dict[str, object]]) -> dict[str, Any]:
        return render_layout(
            [
                {
                    "type": "data_table",
                    "title": "Queue",
                    "columns": [{"key": "id", "label": "ID"}],
                    "rows": [{"id": {"label": "001"}}],
                    "pagination": {"pages": pages},
                }
            ]
        )[0]["pagination"]

    assert pagination_for([])["pages"] == []
    assert [item["label"] for item in pagination_for([page(1, True)])["pages"]] == ["1"]
    assert [
        item["label"]
        for item in pagination_for([page(1), page(2, True), page(3)])["pages"]
    ] == ["1", "2", "3"]

    first_seven = pagination_for([page(number, number == 1) for number in range(1, 8)])
    middle_seven = pagination_for([page(number, number == 4) for number in range(1, 8)])
    last_seven = pagination_for([page(number, number == 7) for number in range(1, 8)])

    assert [item.get("label") for item in first_seven["pages"]] == ["1", "2", None, "7"]
    assert first_seven["pages"][0]["active"] is True
    assert [item.get("label") for item in middle_seven["pages"]] == [
        "1",
        None,
        "3",
        "4",
        "5",
        None,
        "7",
    ]
    assert middle_seven["pages"][3]["active"] is True
    assert [item.get("label") for item in last_seven["pages"]] == ["1", None, "6", "7"]
    assert last_seven["pages"][3]["active"] is True

    first = pagination_for([page(number, number == 1) for number in range(1, 135)])
    last = pagination_for([page(number, number == 134) for number in range(1, 135)])

    assert [item.get("label") for item in first["pages"]] == ["1", "2", None, "134"]
    assert first["next"]["href"] == "/queue?page=2"
    assert [item.get("label") for item in last["pages"]] == ["1", None, "133", "134"]
    assert last["previous"]["href"] == "/queue?page=133"


def test_layout_data_table_badge_cell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Badges",
                "width": 12,
                "columns": [{"key": "status", "label": "Status", "cell": "badge"}],
                "rows": [{"status": {"label": "ok", "tone": "success"}}],
            }
        ]
    )
    cell = result[0]["rows"][0]["status"]
    assert cell["type"] == "badge"
    assert cell["label"] == "ok"
    assert cell["tone"] == "success"


def test_layout_data_table_status_cell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Status",
                "width": 12,
                "columns": [{"key": "s", "label": "S", "cell": "status"}],
                "rows": [{"s": {"label": "Active", "status": "ok"}}],
            }
        ]
    )
    cell = result[0]["rows"][0]["s"]
    assert cell["type"] == "status"
    assert cell["status"] == "ok"


def test_layout_data_table_avatar_text_cell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Avatar",
                "width": 12,
                "columns": [{"key": "owner", "label": "Owner", "cell": "avatar_text"}],
                "rows": [
                    {
                        "owner": {
                            "title": "Operator",
                            "subtitle": "demo@local",
                            "initials": "OP",
                        }
                    }
                ],
            }
        ]
    )
    cell = result[0]["rows"][0]["owner"]
    assert cell["type"] == "avatar_text"
    assert cell["title"] == "Operator"
    assert cell["initials"] == "OP"


def test_layout_data_table_progress_cell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Progress",
                "width": 12,
                "columns": [{"key": "p", "label": "P", "cell": "progress"}],
                "rows": [{"p": {"label": "72%", "value": 72, "color": "green"}}],
            }
        ]
    )
    cell = result[0]["rows"][0]["p"]
    assert cell["type"] == "progress"
    assert cell["value"] == 72
    assert cell["color"] == "green"


def test_layout_data_table_actions_cell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Actions",
                "width": 12,
                "columns": [{"key": "a", "label": "", "cell": "actions"}],
                "rows": [
                    {
                        "a": [
                            {"label": "Open", "href": "/runs/001"},
                            {"label": "Edit", "href": "/runs/001/edit"},
                        ]
                    }
                ],
            }
        ]
    )
    cell = result[0]["rows"][0]["a"]
    assert cell["type"] == "actions"
    assert len(cell["items"]) == 2
    assert cell["items"][0]["href"] == "/runs/001"


def test_layout_data_table_actions_unsafe_link_rejected() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Actions",
                "width": 12,
                "columns": [{"key": "a", "label": "", "cell": "actions"}],
                "rows": [
                    {
                        "a": [
                            {"label": "External", "href": "https://evil.com"},
                            {"label": "Safe", "href": "/runs/001"},
                        ]
                    }
                ],
            }
        ]
    )
    cell = result[0]["rows"][0]["a"]
    assert len(cell["items"]) == 1
    assert cell["items"][0]["href"] == "/runs/001"


def test_layout_data_table_bounded_action_normalizes_confirmation_and_fields() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Actions",
                "width": 12,
                "toolbar": {
                    "actions": [
                        {
                            "action_id": "add_sender",
                            "label": "Add sender",
                            "confirmation": "Confirm sender addition",
                            "args": {"source": "manual"},
                            "fields": [
                                {"name": "sender", "type": "text", "max_length": 12},
                                {"name": "email", "type": "email", "max_length": 999},
                            ],
                        }
                    ]
                },
                "columns": [{"key": "a", "label": "", "cell": "actions"}],
                "rows": [{"a": [{"action_id": "remove_sender", "label": "Remove"}]}],
            }
        ]
    )

    toolbar_action = result[0]["toolbar"]["actions"][0]
    row_action = result[0]["rows"][0]["a"]["items"][0]
    assert toolbar_action["confirmation"] == "Confirm sender addition"
    assert toolbar_action["fields"] == [
        {"name": "sender", "type": "text", "label": "sender", "required": True, "max_length": 12},
        {"name": "email", "type": "email", "label": "email", "required": True, "max_length": 254},
    ]
    assert row_action["action_id"] == "remove_sender"
    assert row_action["confirmation"] == ""


def test_layout_data_table_bounded_action_rejects_unsafe_metadata() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Actions",
                "width": 12,
                "toolbar": {
                    "actions": [
                        {"action_id": "safe", "label": "S" * 257},
                        {"action_id": "unsafe", "label": "Unsafe", "confirmation": "C" * 513},
                        {"action_id": "bad_field", "label": "Bad", "fields": [{"name": "x", "type": "url"}]},
                        {"label": "External", "href": "https://example.test/action"},
                    ]
                },
                "columns": [{"key": "value", "label": "Value"}],
                "rows": [{"value": "ok"}],
            }
        ]
    )

    assert result[0]["toolbar"]["actions"] == []


def test_layout_data_table_missing_values_render_na() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Missing",
                "width": 12,
                "columns": [{"key": "val", "label": "Value", "cell": "text"}],
                "rows": [
                    {"val": None},
                    {"val": ""},
                    {"val": {"label": "exists"}},
                ],
            }
        ]
    )
    assert result[0]["rows"][0]["val"]["value"] == "n/a"
    assert result[0]["rows"][1]["val"]["value"] == "n/a"
    assert result[0]["rows"][2]["val"]["value"] == "exists"


def test_layout_data_table_malformed_columns_preserves_shell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Malformed",
                "width": 12,
                "toolbar": {
                    "fields": [
                        {"type": "text", "name": "q", "value": "keep"},
                    ],
                },
                "columns": "not a list",
                "rows": "not a list",
            }
        ]
    )
    assert len(result) == 1
    assert result[0]["type"] == "data_table"
    assert result[0]["title"] == "Malformed"
    assert result[0]["degraded_error"] is not None
    assert "columns" in result[0]["degraded_error"].lower()
    assert result[0]["toolbar"]["fields"][0]["value"] == "keep"


def test_layout_data_table_malformed_rows_preserves_shell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Malformed",
                "width": 12,
                "columns": [{"key": "id", "label": "ID"}],
                "rows": "not a list",
            }
        ]
    )
    assert len(result) == 1
    assert result[0]["type"] == "data_table"
    assert result[0]["degraded_error"] is not None
    assert "rows" in result[0]["degraded_error"].lower()
    assert result[0]["title"] == "Malformed"


def test_layout_data_table_link_cell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Links",
                "width": 12,
                "columns": [{"key": "link", "label": "Link", "cell": "link"}],
                "rows": [
                    {
                        "link": {
                            "label": "Open run",
                            "href": "/runs/001",
                        }
                    }
                ],
            }
        ]
    )
    cell = result[0]["rows"][0]["link"]
    assert cell["type"] == "link"
    assert cell["href"] == "/runs/001"
    assert cell["label"] == "Open run"


def test_layout_data_table_external_link_cell_rejected() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Links",
                "width": 12,
                "columns": [{"key": "link", "label": "Link", "cell": "link"}],
                "rows": [
                    {
                        "link": {
                            "label": "External",
                            "href": "https://evil.com",
                        }
                    }
                ],
            }
        ]
    )
    cell = result[0]["rows"][0]["link"]
    assert cell["type"] == "link"
    assert cell["href"] is None


def test_layout_data_table_unknown_cell_type() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Unknown",
                "width": 12,
                "columns": [{"key": "x", "label": "X", "cell": "unknown_type"}],
                "rows": [{"x": {"label": "val"}}],
            }
        ]
    )
    cell = result[0]["rows"][0]["x"]
    assert cell["type"] == "text"
    assert cell["value"] == "val"


def test_layout_data_table_template_exists() -> None:
    assert Path(
        "src/beeui_module/web/templates/components/layout/data_table.html"
    ).is_file()


def test_layout_existing_table_card_still_works() -> None:
    result = render_layout(
        [
            {
                "type": "metric_card",
                "title": "Legacy metric",
                "value": "42",
                "width": 3,
            }
        ]
    )
    assert result[0]["type"] == "metric_card"
    assert result[0]["value"] == "42"


def test_layout_data_table_no_product_imports() -> None:
    import beeui_module.blocks.layout_renderer as lr

    content = Path(lr.__file__).read_text(encoding="utf-8")
    assert "beecap_module" not in content
    assert "beeagent_module" not in content


def test_layout_data_table_toolbar_date_range_normalized() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar dates",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "fields": [
                        {
                            "type": "date_range",
                            "name": "dt",
                            "from_value": "2026-07-01",
                            "to_value": "2026-07-31",
                            "from_label": "Start",
                            "to_label": "End",
                        }
                    ]
                },
            }
        ]
    )
    block = result[0]
    fields = block["toolbar"]["fields"]
    assert len(fields) == 1
    dr = fields[0]
    assert dr["type"] == "date_range"
    assert dr["from_value"] == "2026-07-01"
    assert dr["to_value"] == "2026-07-31"
    assert dr["from_label"] == "Start"
    assert dr["to_label"] == "End"
    assert block["toolbar"]["has_date_range"] is True


def test_layout_data_table_toolbar_text_field_normalized() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar text",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "fields": [
                        {
                            "type": "text",
                            "name": "q",
                            "value": "search_val",
                            "placeholder": "Search...",
                        }
                    ]
                },
            }
        ]
    )
    block = result[0]
    field = block["toolbar"]["fields"][0]
    assert field["type"] == "text"
    assert field["name"] == "q"
    assert field["value"] == "search_val"
    assert field["placeholder"] == "Search..."


def test_layout_data_table_toolbar_checkboxes_normalized() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar checkboxes",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "fields": [
                        {
                            "type": "checkboxes",
                            "label": "Status",
                            "choices": [
                                {
                                    "value": "ok",
                                    "label": "OK",
                                    "checked": True,
                                    "toggle_href": "/filter?status=ok",
                                },
                                {
                                    "value": "warn",
                                    "label": "Warning",
                                    "checked": False,
                                    "toggle_href": "/filter?status=warn",
                                },
                            ],
                            "selected_count": 1,
                        }
                    ]
                },
            }
        ]
    )
    field = result[0]["toolbar"]["fields"][0]
    assert field["type"] == "checkboxes"
    assert len(field["choices"]) == 2
    assert field["choices"][0]["checked"] is True
    assert field["choices"][0]["toggle_href"] == "/filter?status=ok"
    assert field["choices"][1]["checked"] is False
    assert field["choices"][1]["toggle_href"] == "/filter?status=warn"
    assert field["selected_count"] == 1


def test_layout_data_table_toolbar_checkboxes_unsafe_toggle_rejected() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar unsafe",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "fields": [
                        {
                            "type": "checkboxes",
                            "choices": [
                                {
                                    "value": "safe",
                                    "label": "Safe",
                                    "toggle_href": "/filter?safe=1",
                                },
                                {
                                    "value": "bad",
                                    "label": "External",
                                    "toggle_href": "https://evil.com",
                                },
                            ],
                        }
                    ]
                },
            }
        ]
    )
    choices = result[0]["toolbar"]["fields"][0]["choices"]
    assert choices[0]["toggle_href"] == "/filter?safe=1"
    assert choices[1]["toggle_href"] is None


def test_layout_data_table_toolbar_column_toggles_normalized() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar toggles",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "column_toggles": [
                        {
                            "key": "id",
                            "label": "ID",
                            "visible": True,
                            "toggle_href": "/toggle?id",
                        },
                        {
                            "key": "name",
                            "label": "Name",
                            "visible": False,
                            "toggle_href": "/toggle?name",
                        },
                    ]
                },
            }
        ]
    )
    toggles = result[0]["toolbar"]["column_toggles"]
    assert len(toggles) == 2
    assert toggles[0]["visible"] is True
    assert toggles[0]["toggle_href"] == "/toggle?id"
    assert toggles[1]["visible"] is False
    assert toggles[1]["toggle_href"] == "/toggle?name"


def test_layout_data_table_toolbar_reset_and_apply_normalized() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar actions",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "reset": {"label": "Clear", "href": "/?reset=1"},
                    "apply": {"label": "Go"},
                },
            }
        ]
    )
    block = result[0]
    assert block["toolbar"]["reset"]["label"] == "Clear"
    assert block["toolbar"]["reset"]["href"] == "/?reset=1"
    assert block["toolbar"]["apply"]["label"] == "Go"


def test_layout_data_table_toolbar_reset_unsafe_href_omitted() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Toolbar reset unsafe",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "reset": {"label": "Reset", "href": "https://evil.com"},
                },
            }
        ]
    )
    reset = result[0]["toolbar"].get("reset", {})
    assert "href" not in reset


def test_layout_data_table_toolbar_apply_absent_when_not_supplied() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "No apply",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {},
            }
        ]
    )
    assert "apply" not in result[0]["toolbar"]


def test_layout_data_table_toolbar_hidden_fields() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Hidden",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "hidden": {"tab": "queue", "view": "list"},
                },
            }
        ]
    )
    assert result[0]["toolbar"]["hidden"] == {"tab": "queue", "view": "list"}


def test_layout_data_table_toolbar_missing_fields_degrades_gracefully() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "No fields",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["toolbar"]["fields"] == []


def test_layout_data_table_toolbar_multiple_field_types_order() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Field order",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "fields": [
                        {"type": "date_range", "name": "d"},
                        {"type": "text", "name": "q"},
                        {"type": "checkboxes", "choices": []},
                    ]
                },
            }
        ]
    )
    fields = result[0]["toolbar"]["fields"]
    assert fields[0]["type"] == "date_range"
    assert fields[1]["type"] == "text"
    assert fields[2]["type"] == "checkboxes"


def test_layout_data_table_toolbar_does_not_have_standalone_date_range_body() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Card test",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
                "toolbar": {
                    "fields": [
                        {
                            "type": "date_range",
                            "from_value": "2026-07-01",
                            "to_value": "2026-07-31",
                        },
                    ]
                },
            }
        ]
    )
    block = result[0]
    assert block["type"] == "data_table"
    assert block["toolbar"]["fields"][0]["type"] == "date_range"
    assert block["toolbar"]["has_date_range"] is True


def test_layout_data_table_sortable_headers_regression() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Sortable",
                "columns": [
                    {
                        "key": "id",
                        "label": "ID",
                        "sortable": True,
                        "sort_href": "/runs?sort=id&dir=asc",
                    },
                    {"key": "name", "label": "Name", "sortable": False},
                ],
                "rows": [
                    {"id": {"label": "001"}, "name": {"label": "Alice"}},
                    {"id": {"label": "002"}, "name": {"label": "Bob"}},
                ],
            }
        ]
    )
    columns = result[0]["columns"]
    assert columns[0]["sortable"] is True
    assert columns[0]["sort_href"] == "/runs?sort=id&dir=asc"
    assert columns[1]["sortable"] is False
    assert columns[1]["sort_href"] is None
    assert "\u2191" not in str(columns)
    assert "\u2193" not in str(columns)


def test_layout_data_table_progress_bounds() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Bounds",
                "width": 12,
                "columns": [{"key": "p", "label": "P", "cell": "progress"}],
                "rows": [
                    {"p": {"label": "-10%", "value": -10}},
                    {"p": {"label": "200%", "value": 200}},
                    {"p": {"label": "50%", "value": 50}},
                ],
            }
        ]
    )
    assert result[0]["rows"][0]["p"]["value"] == 0
    assert result[0]["rows"][1]["p"]["value"] == 100
    assert result[0]["rows"][2]["p"]["value"] == 50


def test_layout_data_table_muted_cell() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Muted",
                "width": 12,
                "columns": [{"key": "x", "label": "X", "cell": "muted"}],
                "rows": [{"x": {"label": "optional"}}],
            }
        ]
    )
    cell = result[0]["rows"][0]["x"]
    assert cell["type"] == "text"
    assert cell["value"] == "optional"
    assert cell["tone"] == "muted"


def test_layout_data_table_visual_tokens_are_whitelisted() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Visual tokens",
                "columns": [
                    {"key": "badge", "label": "Badge", "cell": "badge"},
                    {"key": "status", "label": "Status", "cell": "status"},
                    {"key": "avatar", "label": "Avatar", "cell": "avatar_text"},
                    {"key": "progress", "label": "Progress", "cell": "progress"},
                ],
                "rows": [
                    {
                        "badge": {"label": "Bad", "tone": "danger extra"},
                        "status": {"label": "Bad", "status": "ok extra"},
                        "avatar": {"title": "Bad", "color": "red extra"},
                        "progress": {
                            "label": "Bad",
                            "value": 50,
                            "color": "green extra",
                        },
                    },
                    {
                        "badge": {"label": "Good", "tone": "success"},
                        "status": {"label": "Good", "status": "ok"},
                        "avatar": {"title": "Good", "color": "red"},
                        "progress": {"label": "Good", "value": 50, "color": "green"},
                    },
                ],
            }
        ]
    )

    first = result[0]["rows"][0]
    second = result[0]["rows"][1]

    assert first["badge"]["tone"] == "secondary"
    assert first["status"]["status"] == "unknown"
    assert first["avatar"]["color"] == ""
    assert first["progress"]["color"] == ""

    assert second["badge"]["tone"] == "success"
    assert second["status"]["status"] == "ok"
    assert second["avatar"]["color"] == "red"
    assert second["progress"]["color"] == "green"


# ── filter_form block tests ────────────────────────────────────────────────


def test_filter_form_renders_minimal() -> None:
    """Verify the renderer accepts a minimal filter_form block."""
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "size": "XL",
                "fields": [],
                "actions": {},
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "filter_form"
    assert block["title"] == "Filters"
    assert block["fields"] == []
    assert block["actions"] == {}


def test_filter_form_renders_with_fields() -> None:
    """Verify the renderer preserves filter field definitions."""
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Queue Filters",
                "size": "XL",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "label": "Date range",
                        "from_value": "2026-06-01",
                        "to_value": "2026-06-30",
                    },
                    {
                        "type": "text",
                        "name": "sender",
                        "label": "Sender",
                        "value": "lead@example.com",
                        "placeholder": "Search by sender...",
                    },
                    {
                        "type": "select",
                        "name": "classification",
                        "label": "Classification",
                        "value": "new_lead",
                        "options": [
                            {"value": "new_lead", "label": "New lead"},
                            {"value": "existing_deal", "label": "Existing deal"},
                        ],
                        "multi": True,
                    },
                ],
                "actions": {
                    "apply": {"label": "Apply", "method": "GET"},
                    "reset": {"label": "Reset", "href": "/rop?tab=queue"},
                },
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "filter_form"
    assert block["title"] == "Queue Filters"

    # date_range field
    dr = block["fields"][0]
    assert dr["type"] == "date_range"
    assert dr["from_value"] == "2026-06-01"
    assert dr["to_value"] == "2026-06-30"

    # text field
    txt = block["fields"][1]
    assert txt["type"] == "text"
    assert txt["value"] == "lead@example.com"
    assert txt["placeholder"] == "Search by sender..."

    # select field
    sel = block["fields"][2]
    assert sel["type"] == "select"
    assert sel["value"] == "new_lead"
    assert len(sel["options"]) == 2
    assert sel["multi"] is True

    assert block["actions"]["apply"]["label"] == "Apply"
    assert "method" not in block["actions"]["apply"]
    assert block["actions"]["reset"]["href"] == "/rop?tab=queue"


def test_filter_form_handles_empty_fields_gracefully() -> None:
    """Verify that missing or invalid field data degrades safely."""
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": None,
                "actions": None,
            }
        ]
    )
    assert len(result) == 1
    block = result[0]
    assert block["type"] == "filter_form"
    assert block["fields"] == []
    assert block["actions"] == {}


def test_filter_form_select_handles_invalid_options() -> None:
    """Verify that select field rejects non-dict options."""
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "select",
                        "name": "invalid_opts",
                        "label": "Bad options",
                        "value": "",
                        "options": ["just_a_string", 42, None],
                    }
                ],
                "actions": {},
            }
        ]
    )
    block = result[0]
    sel = block["fields"][0]
    assert sel["options"] == []


def test_data_table_sort_href_preserved() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Sortable",
                "width": 12,
                "columns": [
                    {
                        "key": "id",
                        "label": "ID",
                        "sortable": True,
                        "sort_href": "/runs?sort=id&dir=asc",
                    },
                    {
                        "key": "name",
                        "label": "Name",
                        "sortable": True,
                        "sort_href": None,
                    },
                    {"key": "val", "label": "Value", "sortable": False},
                ],
                "rows": [
                    {
                        "id": {"label": "001"},
                        "name": {"label": "A"},
                        "val": {"label": "1"},
                    }
                ],
            }
        ]
    )
    columns = result[0]["columns"]
    assert columns[0]["sort_href"] == "/runs?sort=id&dir=asc"
    assert columns[1]["sort_href"] is None
    assert columns[2]["sort_href"] is None


def test_data_table_sort_href_unsafe_rejected() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Sortable",
                "width": 12,
                "columns": [
                    {
                        "key": "id",
                        "label": "ID",
                        "sortable": True,
                        "sort_href": "https://evil.com/sort",
                    },
                    {
                        "key": "name",
                        "label": "Name",
                        "sortable": True,
                        "sort_href": "//evil.com/sort",
                    },
                    {
                        "key": "val",
                        "label": "Value",
                        "sortable": True,
                        "sort_href": "/../secret",
                    },
                    {
                        "key": "safe",
                        "label": "Safe",
                        "sortable": True,
                        "sort_href": "/runs?sort=id&dir=asc",
                    },
                ],
                "rows": [
                    {
                        "id": {"label": "001"},
                        "name": {"label": "A"},
                        "val": {"label": "1"},
                        "safe": {"label": "2"},
                    }
                ],
            }
        ]
    )
    columns = result[0]["columns"]
    assert columns[0]["sort_href"] is None
    assert columns[1]["sort_href"] is None
    assert columns[2]["sort_href"] is None
    assert columns[3]["sort_href"] == "/runs?sort=id&dir=asc"


def test_filter_form_checkbox_toggle_href_validated() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "checkboxes",
                        "name": "status",
                        "label": "Status",
                        "choices": [
                            {
                                "value": "ok",
                                "label": "OK",
                                "checked": True,
                                "toggle_href": "/filter?status=ok",
                            },
                            {
                                "value": "bad",
                                "label": "External",
                                "checked": False,
                                "toggle_href": "https://evil.com",
                            },
                            {
                                "value": "bad2",
                                "label": "Proto relative",
                                "checked": False,
                                "toggle_href": "//evil.com",
                            },
                        ],
                    }
                ],
                "actions": {},
            }
        ]
    )
    choices = result[0]["fields"][0]["choices"]
    assert choices[0]["toggle_href"] == "/filter?status=ok"
    assert choices[1]["toggle_href"] is None
    assert choices[2]["toggle_href"] is None


def test_filter_form_reset_href_validated() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "actions": {
                    "reset": {"label": "Reset", "href": "https://evil.com"},
                    "apply": {"label": "Apply", "method": "GET"},
                },
            }
        ]
    )
    block = result[0]
    assert "href" not in block["actions"].get("reset", {})
    assert block["actions"]["apply"]["label"] == "Apply"


def test_filter_form_reset_href_safe() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "actions": {
                    "reset": {"label": "Clear", "href": "/filter?clear=1"},
                },
            }
        ]
    )
    assert result[0]["actions"]["reset"]["href"] == "/filter?clear=1"


def test_filter_form_columns_toggle_href_validated() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "columns_toggle_href": "https://evil.com/toggle",
                "column_toggles": [
                    {
                        "key": "col1",
                        "label": "Col 1",
                        "visible": True,
                        "toggle_href": "/toggle/col1",
                    },
                    {
                        "key": "col2",
                        "label": "Col 2",
                        "visible": False,
                        "toggle_href": "https://evil.com/col2",
                    },
                ],
                "columns_open": True,
                "fields": [],
                "actions": {},
            }
        ]
    )
    block = result[0]
    assert block["columns_toggle_href"] is None
    assert block["column_toggles"][0]["toggle_href"] == "/toggle/col1"
    assert block["column_toggles"][1]["toggle_href"] is None


def test_filter_form_unsafe_href_omitted_from_actions() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "actions": {
                    "apply": {
                        "label": "Apply",
                        "method": "GET",
                        "href": "https://evil.com/apply",
                    },
                },
            }
        ]
    )
    block = result[0]
    assert "href" not in block["actions"].get("apply", {})


def test_layout_links_share_internal_boundary_and_apply_mount_prefix_once() -> None:
    for href in ("/events//item", "/.", "/events%5Citem", "/events/%2e%2e/item"):
        assert validate_internal_href(href) is None

    blocks = render_layout(
        [
            {
                "type": "group",
                "children": [
                    {
                        "type": "filter_form",
                        "title": "Filters",
                        "actions": {
                            "apply": {
                                "label": "Apply",
                                "href": "/rop?apply=1",
                                "method": "POST",
                            },
                            "reset": {"label": "Reset", "href": "/rop?reset=1"},
                        },
                        "columns_toggle_href": "/rop?columns=1",
                        "column_toggles": [
                            {
                                "key": "run",
                                "label": "Run",
                                "toggle_href": "/rop?column=run",
                            }
                        ],
                        "fields": [
                            {
                                "type": "checkboxes",
                                "choices": [
                                    {
                                        "value": "ok",
                                        "label": "OK",
                                        "toggle_href": "/rop?state=ok",
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "type": "data_table",
                        "title": "Rows",
                        "toolbar": {
                            "actions": [{"label": "Open", "href": "/rop?open=1"}]
                        },
                        "columns": [
                            {
                                "key": "run",
                                "label": "Run",
                                "sortable": True,
                                "sort_href": "/rop?sort=run",
                            }
                        ],
                        "rows": [{"run": {"label": "42", "href": "/rop/42"}}],
                        "pagination": {
                            "pages": [{"label": "1", "href": "/rop?page=1"}]
                        },
                    },
                ],
            }
        ]
    )
    resolve_layout_links(blocks, "/ui", "/ui/rop")
    form, table = blocks[0]["children"]
    assert form["form_action"] == "/ui/rop?apply=1"
    assert "method" not in form["actions"]["apply"]
    assert form["actions"]["reset"]["href"] == "/ui/rop?reset=1"
    assert form["fields"][0]["choices"][0]["toggle_href"] == "/ui/rop?state=ok"
    assert form["column_toggles"][0]["toggle_href"] == "/ui/rop?column=run"
    assert table["columns"][0]["sort_href"] == "/ui/rop?sort=run"
    assert table["toolbar"]["actions"][0]["href"] == "/ui/rop?open=1"
    assert table["pagination"]["pages"][0]["href"] == "/ui/rop?page=1"
    assert "/ui/ui/" not in str(blocks)


def test_data_table_sort_metadata_is_atomic() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Rows",
                "columns": [
                    {
                        "key": "plain",
                        "label": "Plain",
                        "sortable": False,
                        "sort_href": "/rows?sort=plain",
                        "sort_active": True,
                        "sort_direction": "asc",
                    },
                    {
                        "key": "missing",
                        "label": "Missing",
                        "sortable": True,
                        "sort_active": True,
                        "sort_direction": "asc",
                    },
                    {
                        "key": "unknown",
                        "label": "Unknown",
                        "sortable": True,
                        "sort_href": "/rows?sort=unknown",
                        "sort_active": True,
                        "sort_direction": "sideways",
                    },
                    {
                        "key": "unsafe",
                        "label": "Unsafe",
                        "sortable": True,
                        "sort_href": "https://invalid.example",
                        "sort_active": True,
                        "sort_direction": "asc",
                    },
                    {
                        "key": "agent",
                        "label": "Run",
                        "sortable": True,
                        "sort_href": "/rows?sort=run",
                        "sort_active": True,
                        "sort_direction": "desc",
                    },
                ],
                "rows": [{}],
            }
        ]
    )[0]
    plain, missing, unknown, unsafe, agent = result["columns"]
    assert plain["sort_href"] is None and not plain["sort_active"]
    assert missing["sort_href"] is None and not missing["sort_active"]
    assert unknown["sort_href"] == "/rows?sort=unknown" and not unknown["sort_active"]
    assert unsafe["sort_href"] is None and not unsafe["sort_active"]
    assert agent["sort_active"] and agent["sort_direction"] == "descending"


def test_chart_metadata_is_bounded_and_operator_progress_is_safe() -> None:
    result = render_layout(
        [
            {
                "type": "chart",
                "title": "Chart",
                "kind": "bar",
                "chart_id": "bad id<script>",
                "colors": ["primary", "success", "<script>"] + ["danger"] * 20,
                "horizontal": "false",
                "barHeight": "1000px",
                "series": [{"name": "Series", "data": [1]}],
            },
            {
                "type": "operator_hero",
                "title": "Hero",
                "items": [
                    {
                        "label": "Low",
                        "value": "x",
                        "progress": -1,
                        "progress_tone": "bg-success",
                    },
                    {
                        "label": "High",
                        "value": "x",
                        "progress": 101,
                        "progress_tone": "invalid",
                    },
                    {"label": "Bool", "value": "x", "progress": True},
                    {"label": "Nan", "value": "x", "progress": float("nan")},
                    {"label": "Inf", "value": "x", "progress": float("inf")},
                ],
            },
        ]
    )
    chart, hero = result
    assert chart["chart_id"].startswith("beeui-chart-")
    assert (
        chart["chart_config"]["colors"]
        == ["var(--tblr-primary)", "var(--tblr-success)"] + ["var(--tblr-danger)"] * 10
    )
    assert chart["chart_config"]["plotOptions"]["bar"]["columnWidth"] == "55%"
    assert "barHeight" not in chart["chart_config"]["plotOptions"]["bar"]
    items = hero["items"]
    assert items[0]["progress"] == 0 and items[0]["progress_tone"] == "bg-success"
    assert items[1]["progress"] == 100 and items[1]["progress_tone"] == "bg-primary"
    assert all("progress" not in item for item in items[2:])


def test_data_table_progress_requires_finite_numeric_values() -> None:
    values = [float("nan"), float("inf"), float("-inf"), True, -5, 101, 12.5]
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Rows",
                "columns": [
                    {"key": "progress", "label": "Progress", "cell": "progress"}
                ],
                "rows": [
                    {"progress": {"value": value, "label": "x"}} for value in values
                ],
            }
        ]
    )[0]
    normalized = [row["progress"]["value"] for row in result["rows"]]
    assert normalized == [0, 0, 0, 0, 0, 100, 12.5]


def test_layout_has_date_ranges_detects_filter_form_date_range() -> None:
    from beeui_module.blocks.layout_renderer import layout_has_date_ranges

    blocks = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": "2026-07-01",
                        "to_value": "2026-07-31",
                        "from_label": "From",
                        "to_label": "To",
                    }
                ],
                "actions": {},
            }
        ]
    )
    assert layout_has_date_ranges(blocks) is True


def test_layout_has_date_ranges_detects_nested_group_date_range() -> None:
    from beeui_module.blocks.layout_renderer import layout_has_date_ranges

    blocks = render_layout(
        [
            {
                "type": "group",
                "children": [
                    {
                        "type": "filter_form",
                        "title": "Filters",
                        "fields": [
                            {
                                "type": "date_range",
                                "name": "date",
                                "from_value": "2026-07-01",
                                "to_value": "2026-07-31",
                            }
                        ],
                        "actions": {},
                    }
                ],
            }
        ]
    )
    assert layout_has_date_ranges(blocks) is True


def test_layout_has_date_ranges_no_date_range() -> None:
    from beeui_module.blocks.layout_renderer import layout_has_date_ranges

    blocks = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "text",
                        "name": "q",
                        "value": "search",
                    }
                ],
                "actions": {},
            }
        ]
    )
    assert layout_has_date_ranges(blocks) is False


def test_layout_has_date_ranges_empty_blocks() -> None:
    from beeui_module.blocks.layout_renderer import layout_has_date_ranges

    assert layout_has_date_ranges([]) is False
    assert layout_has_date_ranges([{"type": "chart", "title": "C"}]) is False
    assert layout_has_date_ranges([{"type": "degraded", "reason": "bad"}]) is False


def test_layout_has_date_ranges_only_one_date_field() -> None:
    from beeui_module.blocks.layout_renderer import layout_has_date_ranges

    blocks = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": "2026-07-01",
                    }
                ],
                "actions": {},
            }
        ]
    )
    assert layout_has_date_ranges(blocks) is True

    blocks2 = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "to_value": "2026-07-31",
                    }
                ],
                "actions": {},
            }
        ]
    )
    assert layout_has_date_ranges(blocks2) is True


def test_filter_form_date_range_preserves_values() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": "2026-06-01",
                        "to_value": "2026-06-30",
                        "from_label": "From",
                        "to_label": "To",
                    }
                ],
                "actions": {},
            }
        ]
    )
    dr = result[0]["fields"][0]
    assert dr["type"] == "date_range"
    assert dr["from_value"] == "2026-06-01"
    assert dr["to_value"] == "2026-06-30"
    assert dr["from_label"] == "From"
    assert dr["to_label"] == "To"


def test_filter_form_date_range_empty_values() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": "",
                        "to_value": "",
                    }
                ],
                "actions": {},
            }
        ]
    )
    dr = result[0]["fields"][0]
    assert dr["from_value"] == ""
    assert dr["to_value"] == ""


def test_filter_form_date_range_start_only() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": "2026-06-01",
                    }
                ],
                "actions": {},
            }
        ]
    )
    dr = result[0]["fields"][0]
    assert dr["from_value"] == "2026-06-01"
    assert dr["to_value"] == ""


def test_filter_form_date_range_end_only() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "to_value": "2026-06-30",
                    }
                ],
                "actions": {},
            }
        ]
    )
    dr = result[0]["fields"][0]
    assert dr["from_value"] == ""
    assert dr["to_value"] == "2026-06-30"


def test_filter_form_date_range_complete_range() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": "2026-06-01",
                        "to_value": "2026-06-30",
                    }
                ],
                "actions": {},
            }
        ]
    )
    dr = result[0]["fields"][0]
    assert dr["from_value"] == "2026-06-01"
    assert dr["to_value"] == "2026-06-30"


def test_filter_form_date_range_unsafe_values_escaped() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": "<script>bad_from</script>",
                        "to_value": "<script>bad_to</script>",
                        "from_label": "<b>from</b>",
                        "to_label": "<i>to</i>",
                    }
                ],
                "actions": {},
            }
        ]
    )
    dr = result[0]["fields"][0]
    assert dr["from_value"] == "<script>bad_from</script>"
    assert dr["to_value"] == "<script>bad_to</script>"
    assert dr["from_label"] == "<b>from</b>"
    assert dr["to_label"] == "<i>to</i>"


def test_filter_form_date_range_non_string_values() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    {
                        "type": "date_range",
                        "name": "date",
                        "from_value": 42,
                        "to_value": None,
                        "from_label": True,
                        "to_label": 3.14,
                    }
                ],
                "actions": {},
            }
        ]
    )
    dr = result[0]["fields"][0]
    assert dr["from_value"] == "42"
    assert dr["to_value"] == ""
    assert dr["from_label"] == "True"
    assert dr["to_label"] == "3.14"


def test_filter_form_date_range_malformed_safe_degrade() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [
                    "not a dict",
                    None,
                    42,
                    {
                        "type": "date_range",
                        "name": "date",
                    },
                ],
                "actions": {},
            }
        ]
    )
    block = result[0]
    assert block["type"] == "filter_form"
    valid_fields = [f for f in block["fields"] if isinstance(f, dict)]
    assert len(valid_fields) == 1
    assert valid_fields[0]["type"] == "date_range"


def test_data_table_toolbar_fields_normalized() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {
                    "fields": [
                        {
                            "type": "date_range",
                            "name": "date",
                            "label": "Period",
                            "from_value": "2026-07-01",
                            "to_value": "2026-07-31",
                            "from_label": "Start",
                            "to_label": "End",
                        },
                        {
                            "type": "text",
                            "name": "q",
                            "label": "Search",
                            "value": "",
                            "placeholder": "Search query...",
                        },
                        {
                            "type": "select",
                            "name": "status",
                            "label": "Status",
                            "value": "new",
                            "options": [
                                {"value": "new", "label": "New"},
                                {"value": "done", "label": "Done"},
                            ],
                        },
                        {
                            "type": "checkboxes",
                            "name": "tags",
                            "label": "Tags",
                            "choices": [
                                {"value": "urgent", "label": "Urgent", "checked": True},
                                {
                                    "value": "review",
                                    "label": "Review",
                                    "checked": False,
                                },
                            ],
                        },
                    ],
                    "hidden": {"tab": "queue"},
                    "column_toggles": [
                        {"key": "id", "label": "ID", "visible": True},
                        {"key": "name", "label": "Name", "visible": False},
                    ],
                    "apply": {"label": "Go"},
                    "reset": {"label": "Clear", "href": "/queue?clear=1"},
                },
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    toolbar = result[0]["toolbar"]
    assert toolbar["fields"][0]["from_value"] == "2026-07-01"
    assert toolbar["fields"][1]["placeholder"] == "Search query..."
    assert toolbar["fields"][2]["value"] == "new"
    assert toolbar["fields"][3]["choices"][0]["checked"] is True
    assert toolbar["hidden"] == {"tab": "queue"}
    assert len(toolbar["column_toggles"]) == 2
    assert toolbar["apply"]["label"] == "Go"
    assert toolbar["reset"]["href"] == "/queue?clear=1"
    assert toolbar.get("search") is False
    assert toolbar.get("entries") is False
    assert toolbar.get("actions") == []


def test_data_table_toolbar_fields_empty_by_default() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Plain table",
                "width": 12,
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    toolbar = result[0]["toolbar"]
    assert toolbar["fields"] == []
    assert toolbar["hidden"] == {}
    assert toolbar["column_toggles"] == []


def test_data_table_toolbar_no_implicit_apply() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {"fields": [{"type": "date_range", "name": "date"}]},
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert "apply" not in result[0]["toolbar"]


def test_data_table_toolbar_explicit_apply() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {"apply": {"label": "Search"}},
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["toolbar"]["apply"]["label"] == "Search"


def test_data_table_toolbar_unsafe_hrefs_rejected() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {
                    "columns_toggle_href": "https://evil.com/toggle",
                    "column_toggles": [
                        {
                            "key": "id",
                            "label": "ID",
                            "toggle_href": "https://evil.com/id",
                        },
                        {"key": "name", "label": "Name", "toggle_href": "/safe/name"},
                    ],
                    "reset": {"label": "Reset", "href": "https://evil.com/reset"},
                    "apply": {"label": "Apply", "href": "https://evil.com/apply"},
                    "fields": [
                        {
                            "type": "checkboxes",
                            "name": "tags",
                            "choices": [
                                {
                                    "value": "ok",
                                    "label": "OK",
                                    "toggle_href": "https://evil.com/ok",
                                },
                                {
                                    "value": "safe",
                                    "label": "Safe",
                                    "toggle_href": "/safe/toggle",
                                },
                            ],
                        }
                    ],
                },
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    toolbar = result[0]["toolbar"]
    assert toolbar["column_toggles"][0]["toggle_href"] is None
    assert toolbar["column_toggles"][1]["toggle_href"] == "/safe/name"
    assert "href" not in toolbar.get("reset", {})
    assert "href" not in toolbar.get("apply", {})
    assert toolbar["fields"][0]["choices"][0]["toggle_href"] is None
    assert toolbar["fields"][0]["choices"][1]["toggle_href"] == "/safe/toggle"


def test_data_table_toolbar_malformed_fields_degrade_safely() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {
                    "fields": "not a list",
                    "hidden": "not a dict",
                    "column_toggles": "not a list",
                    "apply": "not a dict",
                    "reset": None,
                },
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "data_table"
    assert block["toolbar"]["fields"] == []
    assert block["toolbar"]["hidden"] == {}
    assert block["toolbar"]["column_toggles"] == []


def test_data_table_toolbar_legacy_search_entries_preserved() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Legacy",
                "width": 12,
                "toolbar": {
                    "search": True,
                    "entries": True,
                    "actions": [{"label": "Export", "href": "/export"}],
                },
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    toolbar = result[0]["toolbar"]
    assert toolbar["search"] is True
    assert toolbar["entries"] is True
    assert len(toolbar["actions"]) == 1


def test_data_table_toolbar_fields_date_range_detected() -> None:
    from beeui_module.blocks.layout_renderer import layout_has_date_ranges

    blocks = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {"fields": [{"type": "date_range", "name": "date"}]},
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert layout_has_date_ranges(blocks) is True


def test_data_table_toolbar_route_prefix_applied_exactly_once() -> None:
    blocks = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {
                    "column_toggles": [
                        {"key": "id", "label": "ID", "toggle_href": "/toggle/id"}
                    ],
                    "reset": {"label": "Reset", "href": "/queue?reset=1"},
                    "apply": {"label": "Apply", "href": "/queue?apply=1"},
                    "fields": [
                        {
                            "type": "checkboxes",
                            "name": "tags",
                            "choices": [
                                {
                                    "value": "ok",
                                    "label": "OK",
                                    "toggle_href": "/toggle/ok",
                                }
                            ],
                        }
                    ],
                },
                "columns": [
                    {
                        "key": "id",
                        "label": "ID",
                        "cell": "link",
                        "sortable": True,
                        "sort_href": "/queue?sort=id",
                    }
                ],
                "rows": [{"id": {"label": "001", "href": "/queue/001"}}],
                "pagination": {
                    "pages": [{"label": "1", "href": "/queue?page=1"}],
                    "page_size": {
                        "options": [{"label": "25", "href": "/queue?size=25"}]
                    },
                },
            }
        ]
    )
    resolve_layout_links(blocks, "/ui", "/ui/queue")
    block = blocks[0]
    assert block["form_action"] == "/ui/queue?apply=1"
    assert block["toolbar"]["column_toggles"][0]["toggle_href"] == "/ui/toggle/id"
    assert block["toolbar"]["reset"]["href"] == "/ui/queue?reset=1"
    assert block["toolbar"]["apply"]["href"] == "/ui/queue?apply=1"
    assert block["toolbar"]["fields"][0]["choices"][0]["toggle_href"] == "/ui/toggle/ok"
    assert block["columns"][0]["sort_href"] == "/ui/queue?sort=id"
    assert block["rows"][0]["id"]["href"] == "/ui/queue/001"
    assert block["pagination"]["pages"][0]["href"] == "/ui/queue?page=1"
    assert block["pagination"]["page_size"]["options"][0]["href"] == "/ui/queue?size=25"


def test_data_table_toolbar_no_double_prefix() -> None:
    blocks = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {
                    "column_toggles": [
                        {"key": "id", "label": "ID", "toggle_href": "/toggle/id"}
                    ],
                    "reset": {"label": "Reset", "href": "/reset"},
                    "apply": {"label": "Apply", "href": "/apply"},
                    "fields": [
                        {
                            "type": "checkboxes",
                            "name": "tags",
                            "choices": [
                                {
                                    "value": "ok",
                                    "label": "OK",
                                    "toggle_href": "/toggle/ok",
                                }
                            ],
                        }
                    ],
                },
                "columns": [
                    {
                        "key": "id",
                        "label": "ID",
                        "cell": "link",
                        "sortable": True,
                        "sort_href": "/sort",
                    }
                ],
                "rows": [{"id": {"label": "001", "href": "/row/001"}}],
                "pagination": {"pages": [{"label": "1", "href": "/page?p=1"}]},
            }
        ]
    )
    resolve_layout_links(blocks, "/ui", "/ui/queue")
    resolve_layout_links(blocks, "/ui", "/ui/queue")
    block = blocks[0]
    assert "/ui/ui/" not in str(blocks)
    assert block["form_action"] == "/ui/apply"
    assert block["toolbar"]["reset"]["href"] == "/ui/reset"


def test_data_table_toolbar_resolve_links_form_action_default() -> None:
    blocks = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": {"fields": [{"type": "text", "name": "q"}]},
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    resolve_layout_links(blocks, "/ui", "/ui/queue")
    assert blocks[0]["form_action"] == "/ui/queue"


def test_data_table_toolbar_malformed_toolbar_degrades_safely() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Queue",
                "width": 12,
                "toolbar": "not a dict",
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    block = result[0]
    assert block["type"] == "data_table"
    assert block["toolbar"]["fields"] == []
    assert block["toolbar"]["hidden"] == {}
    assert block["toolbar"]["column_toggles"] == []


def test_data_table_toolbar_legacy_search_inert() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Legacy",
                "width": 12,
                "toolbar": {"search": True},
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["toolbar"]["search"] is True
    assert result[0]["toolbar"]["fields"] == []


def test_data_table_toolbar_legacy_entries_inert() -> None:
    result = render_layout(
        [
            {
                "type": "data_table",
                "title": "Legacy",
                "width": 12,
                "toolbar": {"entries": True},
                "columns": [{"key": "id", "label": "ID"}],
                "rows": [{"id": {"label": "001"}}],
            }
        ]
    )
    assert result[0]["toolbar"]["entries"] is True
    assert result[0]["toolbar"]["fields"] == []


def test_filter_form_no_implicit_apply() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [{"type": "date_range", "name": "date"}],
                "actions": {},
            }
        ]
    )
    assert result[0]["has_date_range"] is True
    assert "apply" not in result[0]["actions"]


def test_filter_form_explicit_apply() -> None:
    result = render_layout(
        [
            {
                "type": "filter_form",
                "title": "Filters",
                "fields": [{"type": "date_range", "name": "date"}],
                "actions": {"apply": {"label": "Go"}},
            }
        ]
    )
    assert result[0]["actions"]["apply"]["label"] == "Go"


def test_run_table_layout_renders() -> None:
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
    assert result[0]["type"] == "run_table"
    assert result[0]["title"] == "Recent Runs"


def test_status_table_layout_renders() -> None:
    result = render_layout(
        [
            {
                "type": "status_table",
                "title": "Health",
                "width": 6,
                "columns": ["Source", "Status", "Reason"],
                "rows": [["runtime/active.json", "missing", "No active runtime"]],
            }
        ]
    )
    assert result[0]["type"] == "status_table"


def test_event_table_layout_renders() -> None:
    result = render_layout(
        [
            {
                "type": "event_table",
                "title": "Events",
                "width": 12,
                "columns": ["Time", "Event"],
                "rows": [["2026-06-01", "Started"]],
            }
        ]
    )
    assert result[0]["type"] == "event_table"
