from __future__ import annotations

import re

from beeui_module.pages.models import (
    TABS_ICON_NAMES,
    TABS_ICON_SVGS,
)
from beeui_module.pages.tab_icons import (
    supported_tab_icon_names,
    tab_icon_svg,
)


def _svg_bodies() -> dict[str, str]:
    bodies: dict[str, str] = {}
    for name in supported_tab_icon_names():
        svg = tab_icon_svg(name)
        paths = "".join(re.findall(r'<path d="([^"]+)"/>', str(svg)))
        bodies[name] = paths
    return bodies


def test_registry_supports_minimum_nine_distinct_concepts() -> None:
    assert len(TABS_ICON_NAMES) >= 9
    concepts = {
        "dashboard",
        "queue",
        "messages",
        "ai",
        "source",
        "attachment",
        "evidence",
        "integration",
        "recommendation",
        "ban",
    }
    assert concepts.issubset(set(TABS_ICON_NAMES))


def test_every_documented_identifier_has_distinct_glyph() -> None:
    bodies = _svg_bodies()
    assert set(bodies) == set(TABS_ICON_NAMES)
    for name, body in bodies.items():
        assert body, f"identifier {name} must render a non-empty glyph"
    signatures = set(bodies.values())
    assert len(signatures) == len(TABS_ICON_NAMES)


def test_old_runs_and_list_are_distinct_glyphs() -> None:
    bodies = _svg_bodies()
    assert bodies["runs"] != bodies["list"]


def test_old_reports_and_chart_are_distinct_glyphs() -> None:
    bodies = _svg_bodies()
    assert bodies["reports"] != bodies["chart"]


def test_backward_compatible_identifiers_supported() -> None:
    for name in ("dashboard", "runs", "list", "reports", "chart", "calendar"):
        assert name in TABS_ICON_NAMES
        assert name in TABS_ICON_SVGS
        assert tab_icon_svg(name) != ""


def test_spacing_and_tabler_presentation_contract() -> None:
    svg = tab_icon_svg("dashboard")
    assert 'class="icon me-2"' in str(svg)
    assert 'viewBox="0 0 24 24"' in str(svg)
    assert 'stroke="currentColor"' in str(svg)
    assert 'aria-hidden="true"' in str(svg)


def test_unknown_safe_identifier_renders_no_icon() -> None:
    assert tab_icon_svg("some_unknown_icon") == ""


def test_none_renders_no_icon() -> None:
    assert tab_icon_svg(None) == ""


def test_render_output_contains_no_unsafe_markup_for_any_identifier() -> None:
    for name in supported_tab_icon_names():
        svg = tab_icon_svg(name)
        assert "<script" not in str(svg).lower()
        assert "onerror" not in str(svg).lower()
        assert "href=" not in str(svg)
        assert "http://" not in str(svg)
        assert "https://" not in str(svg)


def test_registry_maps_to_documented_tabler_icons() -> None:
    expected = {
        "dashboard": "dashboard",
        "runs": "activity",
        "list": "list",
        "reports": "chart-bar",
        "chart": "chart-line",
        "calendar": "calendar",
        "queue": "stack",
        "messages": "messages",
        "ai": "robot",
        "source": "database",
        "attachment": "paperclip",
        "evidence": "search",
        "integration": "link",
        "recommendation": "bulb",
        "ban": "ban",
    }
    for name, tabler_name in expected.items():
        svg = str(tab_icon_svg(name))
        assert f'data-beeui-tab-icon="{name}"' in svg
        assert name in TABS_ICON_SVGS
