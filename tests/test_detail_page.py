from __future__ import annotations

import re

from fastapi import Request
from fastapi.testclient import TestClient

from beeui_module.core.paths import settings_path
from beeui_module.pages.config import load_beeui_config
from beeui_module.pages.locale import translate
from beeui_module.web.app import create_beeui_app


def _response_body_text(response) -> str:
    return bytes(response.body).decode("utf-8")


def test_detail_page_renders_title_subtitle_back_href() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "event_detail",
        "title": "Event Detail",
        "subtitle": "Read-only event details",
        "back_href": "/events",
        "warnings": [],
        "sections": [],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert "Event Detail" in body
    assert "Read-only event details" in body
    assert 'href="/events"' in body


def test_detail_page_key_value_section_renders() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "Summary",
                "kind": "key_value",
                "items": [
                    {"label": "Subject", "value": "Test subject"},
                    {"label": "Sender", "value": "test@example.com"},
                    {
                        "label": "Entity ID",
                        "value": "199324",
                        "href": "/entities/199324",
                    },
                    {
                        "label": "Unsafe entity",
                        "value": "199325",
                        "href": "https://unsafe.example/199325",
                    },
                ],
            }
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert "Summary" in body
    assert "Subject" in body
    assert "Test subject" in body
    assert "Sender" in body
    assert "test@example.com" in body
    assert 'href="/entities/199324"' in body
    assert 'href="https://unsafe.example/199325"' not in body


def test_detail_page_text_section_renders() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "Preview",
                "kind": "text",
                "body": "This is a text body with multiple\nlines.",
            }
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert "Preview" in body
    assert "This is a text body with multiple" in body


def test_detail_page_table_section_renders() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "Rows",
                "kind": "table",
                "columns": [
                    {"key": "name", "label": "Name", "cell": "link"},
                    {"key": "value", "label": "Value"},
                ],
                "rows": [
                    {
                        "name": {"label": "Status", "href": "/events/evt_001"},
                        "value": "ok",
                    },
                    {
                        "name": {"label": "Unsafe", "href": "javascript:alert(1)"},
                        "value": "42",
                    },
                ],
            }
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert "Rows" in body
    assert "Name" in body
    assert "Value" in body
    assert "Status" in body
    assert 'href="/events/evt_001"' in body
    assert "javascript:alert" not in body
    assert "ok" in body
    assert "42" in body


def test_detail_page_links_section_renders_internal_links() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "Links",
                "kind": "links",
                "items": [
                    {"label": "Open source", "href": "/runs/run_001"},
                    {"label": "View details", "href": "/events/evt_001"},
                ],
            }
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert "Links" in body
    assert 'href="/runs/run_001"' in body
    assert 'href="/events/evt_001"' in body
    assert "Open source" in body
    assert "View details" in body


def test_detail_page_hrefs_preserve_allowlisted_query_params_and_route_prefix() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "back_href": "/events",
        "sections": [
            {
                "title": "Links",
                "kind": "links",
                "items": [
                    {"label": "Safe", "href": "/events/evt_001"},
                ],
            }
        ],
    }

    request = MagicMock()
    request.query_params = {
        "lang": "ru",
        "period": "24h",
        "run_id": "run_001",
        "secret": "leak-me",
    }

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="/ui",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert 'href="/ui/events?lang=ru&amp;period=24h&amp;run_id=run_001"' in body
    assert 'href="/ui/events/evt_001?lang=ru&amp;period=24h&amp;run_id=run_001"' in body
    assert "secret=leak-me" not in body


def test_detail_page_unsafe_internal_looking_hrefs_are_inert() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "back_href": "/events\\evt_002",
        "sections": [
            {
                "title": "Links",
                "kind": "links",
                "items": [
                    {"label": "Safe", "href": "/events/evt_001"},
                    {"label": "Backslash", "href": "/events\\evt_002"},
                    {"label": "Traversal", "href": "/events/../admin"},
                    {"label": "Double slash", "href": "/events//evt_003"},
                    {"label": "Encoded traversal", "href": "/events/%2e%2e/admin"},
                ],
            }
        ],
    }

    request = MagicMock()
    request.query_params = {
        "lang": "bad",
        "period": "24h",
        "run_id": "run_001",
        "secret": "leak-me",
    }

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert 'href="/events?period=24h&amp;run_id=run_001"' not in body
    assert 'href="/events/evt_001?period=24h&amp;run_id=run_001"' in body
    assert 'href="/events\\\\evt_002' not in body
    assert 'href="/events/../admin' not in body
    assert 'href="/events//evt_003' not in body
    assert 'href="/events/%2e%2e/admin' not in body
    assert '<span class="list-group-item text-secondary">Backslash</span>' in body
    assert '<span class="list-group-item text-secondary">Traversal</span>' in body
    assert '<span class="list-group-item text-secondary">Double slash</span>' in body
    assert (
        '<span class="list-group-item text-secondary">Encoded traversal</span>' in body
    )
    assert "secret=leak-me" not in body


def test_detail_page_unsafe_external_links_omitted() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "Links",
                "kind": "links",
                "items": [
                    {"label": "Safe", "href": "/events/evt_001"},
                    {"label": "External", "href": "https://evil.com/steal"},
                    {"label": "Protocol relative", "href": "//evil.com/steal"},
                    {"label": "JavaScript", "href": "javascript:alert(1)"},
                ],
            }
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert 'href="/events/evt_001"' in body
    assert "https://evil.com" not in body
    assert "//evil.com" not in body
    assert "javascript:alert" not in body


def test_detail_page_unsafe_text_is_escaped() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "Unsafe",
                "kind": "key_value",
                "items": [
                    {
                        "label": '<script>alert("x")</script>',
                        "value": '<img src=x onerror="alert(1)">',
                    }
                ],
            },
            {
                "title": "Text",
                "kind": "text",
                "body": "<script>alert(2)</script>",
            },
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert "<script>alert" not in body
    assert "<img src=x" not in body
    assert "&lt;script&gt;alert" in body
    assert "&lt;img src=x" in body


def test_detail_page_unsupported_section_does_not_crash() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "Unknown",
                "kind": "unknown_kind",
                "items": [{"label": "X", "value": "Y"}],
            },
            {
                "title": "Malformed",
                "kind": "key_value",
            },
            {"title": "Not a dict"},
            "string section",
            42,
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert response.status_code == 200
    assert "Unknown" not in body
    assert "Malformed" not in body
    assert "No content" in body
    assert "Test" in body


def test_detail_page_missing_values_render_as_n_a() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")

    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True

    detail_data = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {
                "title": "KV",
                "kind": "key_value",
                "items": [
                    {"label": "Missing value"},
                    {"label": "Null value", "value": None},
                    {"label": "Normal", "value": "works"},
                ],
            }
        ],
    }

    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page=detail_data,
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI Demo",
        product_id="demo",
    )
    body = _response_body_text(response)
    assert "n/a" in body
    assert "works" in body


def test_detail_display_is_used_for_long_and_automatic_collapsible_content() -> None:
    from unittest.mock import MagicMock

    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.web.app import _resolve_templates_dir

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True
    request = MagicMock()
    request.query_params = {}

    response = render_beeui_detail_page(
        request=request,
        page={
            "page_id": "detail",
            "title": "Detail",
            "sections": [
                {
                    "kind": "key_value",
                    "items": [
                        {
                            "label": "Long",
                            "value": "RAW_LONG_MARKER",
                            "display": "<b>Safe long text</b>",
                            "variant": "long_text",
                            "collapsible": True,
                        },
                        {
                            "label": "Automatic",
                            "value": "RAW_AUTO_MARKER",
                            "display": "<i>" + ("safe" * 80) + "</i>",
                        },
                        {
                            "label": "Message text",
                            "value": "RAW_MODAL_MARKER",
                            "display": "<script>unsafe()</script>",
                            "variant": "modal_text",
                            "modal_trigger_label": "<b>Trigger</b>",
                            "modal_title": "<i>Title</i>",
                            "modal_fields": [
                                {
                                    "label": "<em>Field</em>",
                                    "value": "<script>field()</script>",
                                    "multiline": True,
                                }
                            ],
                        },
                    ],
                }
            ],
        },
        templates=templates,
        route_prefix="",
        ui_config=ui_config,
        product_title="BeeUI",
        product_id="beeui",
    )
    body = _response_body_text(response)

    assert "RAW_LONG_MARKER" not in body
    assert "RAW_AUTO_MARKER" not in body
    assert "RAW_MODAL_MARKER" not in body
    assert "&lt;b&gt;Safe long text&lt;/b&gt;" in body
    assert 'data-bs-toggle="modal"' in body
    assert "modal-dialog modal-dialog-centered modal-dialog-scrollable" in body
    assert 'class="btn btn-sm"' in body
    assert 'class="btn btn-primary btn-sm"' not in body
    assert 'class="btn btn-outline-' not in body
    assert 'class="btn btn-ghost-' not in body
    assert 'class="modal-content beeui-detail-modal"' in body
    assert 'class="btn me-auto"' in body
    assert "Save changes" not in body
    css = (_resolve_templates_dir().parent / "static" / "css" / "beeui.css").read_text(
        encoding="utf-8"
    )
    assert ".modal-content > .modal-header" in css
    assert "border-bottom: 1px solid var(--beeui-border-light);" in css
    assert ".modal-content > .modal-footer" in css
    assert "border-top: 1px solid var(--beeui-border-light);" in css
    assert "unsafe()" not in body
    assert "&lt;b&gt;Trigger&lt;/b&gt;" in body
    assert "&lt;i&gt;Title&lt;/i&gt;" in body
    assert "&lt;em&gt;Field&lt;/em&gt;" in body
    assert "&lt;script&gt;field()&lt;/script&gt;" in body
    assert "&lt;i&gt;" in body


def test_detail_modal_text_normalizes_optional_metadata() -> None:
    from beeui_module.pages.detail import normalize_detail_page

    page = normalize_detail_page(
        {
            "page_id": "detail",
            "title": "Detail",
            "sections": [
                {
                    "kind": "key_value",
                    "items": [
                        {
                            "label": "Text",
                            "value": "value",
                            "variant": "modal_text",
                            "modal_trigger_label": "Show",
                            "modal_title": "Title",
                            "modal_fields": [
                                {"label": "Field", "value": "Value"},
                                {"label": "Body", "value": "Text", "multiline": True},
                                {"label": "", "value": "ignored"},
                                "ignored",
                            ],
                        }
                    ],
                }
            ],
        }
    )

    item = page["sections"][0]["items"][0]
    assert item["modal_trigger_label"] == "Show"
    assert item["modal_title"] == "Title"
    assert item["modal_fields"] == [
        {"label": "Field", "value": "Value", "multiline": False},
        {"label": "Body", "value": "Text", "multiline": True},
    ]


def test_detail_page_raw_extra_fields_not_rendered() -> None:
    from beeui_module.pages.detail import normalize_detail_page

    raw = {
        "page_id": "test",
        "title": "Test",
        "raw_eml": "RAW EMAIL CONTENT",
        "attachment_content": b"BINARY DATA",
        "payload_bytes": b"\x00\x01\x02",
        "content_bytes": b"SECRET CONTENT",
        "sections": [
            {
                "title": "Summary",
                "kind": "key_value",
                "items": [{"label": "Status", "value": "ok"}],
            }
        ],
    }

    normalized = normalize_detail_page(raw)

    assert "raw_eml" not in normalized
    assert "attachment_content" not in normalized
    assert "payload_bytes" not in normalized
    assert "content_bytes" not in normalized
    assert normalized["title"] == "Test"


def test_detail_page_ghost_section_omitted() -> None:
    from beeui_module.pages.detail import normalize_detail_page

    raw = {
        "page_id": "test",
        "title": "Test",
        "sections": [
            {"title": "Empty KV", "kind": "key_value", "items": []},
            {"title": "Empty table", "kind": "table", "columns": [], "rows": []},
            {"title": "Empty links", "kind": "links", "items": []},
        ],
    }

    normalized = normalize_detail_page(raw)

    assert len(normalized["sections"]) == 0


def test_detail_type_hint_legacy_aliases_are_neutral() -> None:
    from beeui_module.pages.detail import normalize_detail_page

    normalized = normalize_detail_page(
        {
            "page_id": "event",
            "title": "Event",
            "sections": [
                {
                    "kind": "key_value",
                    "items": [
                        {"label": "Body", "value": "text", "type_hint": "long_text"},
                        {"label": "Enabled", "value": True, "type_hint": "boolean"},
                        {"label": "Score", "value": 0.8, "type_hint": "confidence"},
                        {
                            "label": "Priority",
                            "value": "high",
                            "type_hint": "priority",
                            "tone": "danger",
                        },
                        {
                            "label": "Other",
                            "value": "x",
                            "type_hint": "unknown",
                            "tone": "warning",
                        },
                    ],
                }
            ],
        }
    )

    items = normalized["sections"][0]["items"]
    assert [item["variant"] for item in items] == [
        "long_text",
        "boolean",
        "confidence",
        "text",
        "text",
    ]
    assert items[3]["tone"] == "default"
    assert items[4]["tone"] == "default"


def test_detail_explicit_variant_takes_priority_over_type_hint() -> None:
    from beeui_module.pages.detail import normalize_detail_page

    normalized = normalize_detail_page(
        {
            "page_id": "event",
            "title": "Event",
            "sections": [
                {
                    "kind": "key_value",
                    "items": [
                        {
                            "label": "Value",
                            "value": "x",
                            "variant": "badge",
                            "type_hint": "long_text",
                            "tone": "success",
                        }
                    ],
                }
            ],
        }
    )

    item = normalized["sections"][0]["items"][0]
    assert item["variant"] == "badge"
    assert item["tone"] == "success"


def test_mounted_detail_links_use_effective_prefix_once() -> None:
    from fastapi import FastAPI
    from fastapi.templating import Jinja2Templates

    from beeui_module.pages.detail import render_beeui_detail_page
    from beeui_module.pages.locale import translate
    from beeui_module.web.app import _resolve_templates_dir, create_beeui_app

    ui_config = load_beeui_config(settings_path().parent / "schema.yml")
    child = create_beeui_app(ui_config=ui_config)
    templates = Jinja2Templates(directory=str(_resolve_templates_dir()))
    templates.env.autoescape = True
    templates.env.globals["translate"] = translate

    @child.get("/detail", include_in_schema=False)
    async def detail(request: Request):
        return render_beeui_detail_page(
            request=request,
            page={
                "page_id": "detail",
                "title": "Detail",
                "back_href": "/runs",
                "sections": [
                    {
                        "kind": "links",
                        "items": [
                            {"label": "Safe", "href": "/runs/one"},
                            {"label": "Unsafe", "href": "https://invalid.example"},
                        ],
                    }
                ],
            },
            templates=templates,
            route_prefix="",
            ui_config=ui_config,
            product_title="Test",
            product_id="test",
        )

    parent = FastAPI()
    parent.mount("/ui", child)
    response = TestClient(parent).get("/ui/detail")

    assert response.status_code == 200
    assert 'href="/ui/runs"' in response.text
    assert 'href="/ui/runs/one"' in response.text
    assert "invalid.example" not in response.text
    assert not re.search(r'<a[^>]+href="[^"]+"[^>]*>\s*Unsafe\s*</a>', response.text)
    assert "/ui/ui/" not in response.text
