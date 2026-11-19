import json
from copy import deepcopy
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jinja2 import Environment, FileSystemLoader, select_autoescape

from beeui_module.adapters.envelopes import ok_result
from beeui_module.artifacts.redaction import redact_value
from beeui_module.auth.models import UserRole
from beeui_module.auth.service import AuthService
from beeui_module.blocks.chat_workspace import (
    normalize_messages,
    render_chat_workspace,
    resolve_chat_links,
)
from beeui_module.web.uploads import register_upload_routes


def payload():
    action = {
        "action_id": "save_context",
        "label": "Save",
        "disabled": False,
        "args": {"revision": "1"},
        "fields": [
            {
                "name": "credential",
                "type": "secret",
                "value": "NEVER-REFLECT",
                "label": "Credential",
            }
        ],
        "navigate": {"href": "/cases", "param": "id", "result_key": "id"},
    }
    return {
        "id": "chat",
        "new_href": "/cases",
        "composer": {
            "variant": "compact",
            "action_id": "ask",
            "disabled": False,
            "fields": [{"name": "question", "type": "textarea"}],
            "menu": {
                "label": "Context",
                "items": [
                    {
                        "id": "context",
                        "kind": "form",
                        "label": "Context",
                        "action": action,
                    }
                ],
            },
            "chips": [
                {
                    "id": "context",
                    "label": "<script>",
                    "edit": action,
                    "remove": {"action_id": "remove_context", "disabled": False},
                }
            ],
        },
    }


def test_execution_cards_render_identity_progress_and_safe_inspector():
    source = payload()
    message = {
        "id": "run-1",
        "sender": "host",
        "kind": "execution",
        "name": "<img src=x>",
        "status": "RUNNING",
        "timestamp": "2026-11-19T00:00:00+00:00",
        "execution": {
            "tone": "blue",
            "outcome": "Inconclusive",
            "duration_ms": 0,
            "progress": {"completed": 2, "total": 4},
            "metrics": [{"label": "Count", "value": "<script>"}],
            "inspector_href": "/api/execution?id=run-1",
        },
    }
    unknown = deepcopy(message)
    unknown["id"] = "run-2"
    unknown["execution"]["progress"] = {"completed": None, "total": None}
    result = {
        "id": "result-1",
        "sender": "host",
        "kind": "result",
        "name": "Summary",
        "status": "Partial",
        "result": {"href": "/results?id=run-1", "tone": "yellow"},
    }
    source["messages"] = [
        {"id": "question", "sender": "operator", "text": "Hi"},
        message,
        unknown,
        result,
    ]
    block = render_chat_workspace(source, "col-12")
    assert "kind" not in block["messages"][0]
    assert normalize_messages(block["messages"]) == block["messages"]
    resolve_chat_links(block, "/mount/prefix")
    env = Environment(
        loader=FileSystemLoader("src/beeui_module/web/templates"),
        autoescape=select_autoescape(),
    )
    html = env.get_template("components/layout/chat_workspace.html").render(
        block=block, locale="ru"
    )
    assert html.index('data-message-id="question"') < html.index(
        'data-message-id="run-1"'
    )
    assert html.index('data-message-id="run-1"') < html.index('data-message-id="run-2"')
    assert html.count("data-chat-inspector data-loading=") == 1
    assert 'data-chat-inspect="/mount/prefix/api/execution?id=run-1"' in html
    assert 'data-execution-progress max="4" value="2"' in html
    assert "data-execution-progress></progress>" in html
    assert 'class="modal-dialog modal-xl' in html
    assert 'data-message-id="result-1" href="/mount/prefix/results?id=run-1"' in html
    assert 'type="button" data-message-id="run-1" aria-haspopup="dialog"' in html
    assert 'data-bs-title="RUNNING · Inconclusive"' in html
    assert 'aria-label="&lt;img src=x&gt; · RUNNING · Inconclusive"' in html
    assert html.count("data-execution-status") == 2
    assert "0.0 с" in html
    result["result"]["href"] = "//foreign"
    with pytest.raises(ValueError, match="Invalid workspace link"):
        normalize_messages([result])
    assert "<img src=x>" not in html and "<script>" not in html


@pytest.mark.parametrize(
    "execution",
    [
        {"tone": []},
        {"tone": "javascript"},
        {"inspector_href": "/%2e%2e/other"},
        {"inspector_href": "//foreign"},
        {"inspector_href": "https://foreign"},
        {"duration_ms": True},
        {"duration_ms": 10**12 + 1},
        {"progress": {"completed": 1, "total": 0}},
        {"progress": {"completed": 2, "total": 1}},
        {"progress": {"total": 1}},
        {"progress": []},
        {"metrics": [{"label": "x", "value": "y" * 81}]},
        {"metrics": [{"label": "x", "value": "y"}] * 9},
        {"outcome": "x" * 161},
    ],
)
def test_execution_card_rejects_malformed_projection(execution):
    message = {
        "id": "run",
        "sender": "host",
        "kind": "execution",
        "name": "Check",
        "status": "Running",
        "execution": execution,
    }
    with pytest.raises(ValueError):
        normalize_messages([message])


@pytest.mark.parametrize(
    "timestamp",
    ["unknown", "2026-02-31", "2026-11-19T24:00:00Z", "2026-11-19x09:00"],
)
def test_execution_card_rejects_invalid_timestamps(timestamp):
    with pytest.raises(ValueError):
        normalize_messages(
            [
                {
                    "id": "run",
                    "sender": "host",
                    "kind": "execution",
                    "name": "Check",
                    "status": "Running",
                    "timestamp": timestamp,
                    "execution": {},
                }
            ]
        )


def test_interactive_secret_nonreflection_and_prefix():
    source = payload()
    block = render_chat_workspace(source, "col-12")
    assert "NEVER-REFLECT" not in json.dumps(block)
    assert "NEVER-REFLECT" not in json.dumps(redact_value(source))
    resolve_chat_links(block, "/mount/prefix")
    assert (
        block["composer"]["menu"]["items"][0]["action"]["navigate"]["href"]
        == "/mount/prefix/cases"
    )
    env = Environment(
        loader=FileSystemLoader("src/beeui_module/web/templates"),
        autoescape=select_autoescape(),
    )
    html = env.get_template("components/layout/chat_workspace.html").render(block=block)
    assert "NEVER-REFLECT" not in html and "<script>" not in html
    assert html.index("<textarea") < html.index("ti-plus") < html.index("ti-arrow-up")
    assert "data-chat-action" in html


@pytest.mark.parametrize(
    "change",
    [
        {"kind": "javascript"},
        {"id": "../escape"},
        {"id": "__proto__"},
        {"action": {"action_id": "../escape"}},
        {
            "action": {
                "action_id": "upload",
                "navigate": {"href": "//foreign", "param": "id", "result_key": "id"},
            }
        },
    ],
)
def test_untrusted_menu_refusal(change):
    source = payload()
    source["composer"]["menu"]["items"][0].update(change)
    with pytest.raises(ValueError):
        render_chat_workspace(source, "col-12")


def test_bounded_menu_property_inputs():
    for count in range(7, 40):
        source = payload()
        source["composer"]["menu"]["items"] *= count
        with pytest.raises(ValueError):
            render_chat_workspace(source, "col-12")
    for bad in (None, False, 1, [], "text", {"action_id": "a", "args": {"x": []}}):
        source = payload()
        source["composer"]["menu"]["items"][0]["action"] = deepcopy(bad)
        with pytest.raises(ValueError):
            render_chat_workspace(source, "col-12")


def test_registered_upload_auth_csrf_limits_and_embedded_mount():
    calls = []

    def callback(arguments, files, actor):
        calls.append((arguments, files, actor))
        return ok_result({"id": "saved"})

    child = FastAPI()
    service = AuthService(
        {
            "enabled": True,
            "session_secret": "test-only-secret",
            "operator_token": "op",
            "admin_token": "admin",
            "cookie_secure": False,
            "cookie_samesite": "lax",
        }
    )
    child.state.beeui_auth_service = service
    register_upload_routes(
        child, "/prefix", SimpleNamespace(upload_actions={"attach": callback})
    )
    app = FastAPI()
    app.mount("/embed", child)
    client = TestClient(app)
    path = "/embed/prefix/api/actions/upload"
    body = {"action_id": "attach", "payload": '{"revision":"1"}'}
    files = {"files": ("note.txt", b"bounded", "text/plain")}
    assert client.post(path, data=body, files=files).status_code == 401
    viewer, cookie = service.create_principal_session("viewer", UserRole.viewer)
    assert viewer is not None
    assert cookie is not None
    client.cookies.set(service.cookie_name(), cookie)
    assert (
        client.post(
            path, data=body, files=files, headers={"X-CSRF-Token": viewer.csrf_token}
        ).status_code
        == 403
    )
    session, cookie = service.create_principal_session("operator", UserRole.operator)
    assert session is not None
    assert cookie is not None
    client.cookies.set(service.cookie_name(), cookie)
    assert client.post(path, data=body, files=files).status_code == 403
    assert (
        client.post(
            path, data=body, files=files, headers={"X-CSRF-Token": "wrong"}
        ).status_code
        == 403
    )
    assert calls == []
    headers = {"X-CSRF-Token": session.csrf_token}
    assert (
        client.post(
            path, data={**body, "action_id": "foreign"}, files=files, headers=headers
        ).status_code
        == 400
    )
    assert (
        client.post(
            path, data=body, files={"files": ("large", b"x" * 2097153)}, headers=headers
        ).status_code
        == 400
    )
    response = client.post(path, data=body, files=files, headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "saved"
    assert len(calls) == 1 and calls[0][2]["user_id"] == "operator"


def test_context_field_inheritance_is_explicit_and_excludes_secrets():
    source = payload()
    fields = source["composer"]["menu"]["items"][0]["action"]["fields"]
    fields[0]["inherit"] = True
    with pytest.raises(ValueError):
        render_chat_workspace(source, "col-12")
    fields[0].update(type="text", inherit="true")
    with pytest.raises(ValueError):
        render_chat_workspace(source, "col-12")
    fields[0]["inherit"] = True
    block = render_chat_workspace(source, "col-12")
    assert (
        block["composer"]["menu"]["items"][0]["action"]["fields"][0]["inherit"] is True
    )


def test_history_actions_are_bounded_siblings_and_prefix_safe():
    source = payload()
    source["history"] = [
        {
            "id": "owned",
            "title": "<case>",
            "href": "/cases?id=owned",
            "actions": [
                {
                    "action_id": "rename",
                    "label": "Rename",
                    "disabled": False,
                    "fields": [{"name": "title", "type": "text"}],
                    "redirect": "/cases?id=owned",
                },
                {
                    "action_id": "archive",
                    "disabled": False,
                    "confirmation": "Preserve evidence",
                    "redirect": "/cases",
                },
            ],
        }
    ]
    block = render_chat_workspace(source, "col-12")
    resolve_chat_links(block, "/embed")
    assert block["history"][0]["actions"][0]["redirect"] == "/embed/cases?id=owned"
    env = Environment(
        loader=FileSystemLoader("src/beeui_module/web/templates"),
        autoescape=select_autoescape(),
    )
    html = env.get_template("components/layout/chat_workspace.html").render(block=block)
    row = html.split('data-history-id="owned"', 1)[1].split("</nav>", 1)[0]
    assert row.index("</a>") < row.index("<button")
    assert "<case>" not in row and 'data-bs-toggle="dropdown"' in row
    for bad in ("//foreign", "https://foreign", "/../escape"):
        source["history"][0]["actions"][0]["redirect"] = bad
        with pytest.raises(ValueError):
            render_chat_workspace(source, "col-12")
    source["history"][0]["actions"] *= 2
    with pytest.raises(ValueError):
        render_chat_workspace(source, "col-12")


def test_optional_conversation_presentation_context_links_and_dropdown():
    source = payload()
    source["message_style"] = "conversation"
    source["errors"] = {"invalid_target": "Safe localized explanation"}
    source["context"] = {
        "title": "Summary",
        "sections": [
            {
                "id": "case",
                "title": "Case",
                "inline": True,
                "items": [
                    {
                        "id": "child",
                        "label": "Results",
                        "value": "CANDIDATE",
                        "href": "/cases?id=child",
                        "tone": "yellow",
                    }
                ],
            }
        ],
    }
    source["messages"] = [
        {
            "id": "message",
            "sender": "operator",
            "name": "Hidden author",
            "status": "question",
            "text": "Safe text",
            "timestamp": "2026-11-16T12:00:00+00:00",
        }
    ]
    source["composer"]["fields"].append(
        {
            "name": "mode",
            "type": "select",
            "widget": "dropdown",
            "value": "quick",
            "options": [
                {"value": "quick", "label": "Quick"},
                {"value": "deep", "label": "Deep"},
            ],
        }
    )
    block = render_chat_workspace(source, "col-12")
    resolve_chat_links(block, "/embed")
    assert (
        block["context"]["sections"][0]["items"][0]["href"] == "/embed/cases?id=child"
    )
    env = Environment(
        loader=FileSystemLoader("src/beeui_module/web/templates"),
        autoescape=select_autoescape(),
    )
    html = env.get_template("components/layout/chat_workspace.html").render(block=block)
    assert "data-context-inline" in html
    assert 'class="status-dot bg-yellow"' in html
    assert (
        "data-chat-local-time" in html
        and 'datetime="2026-11-16T12:00:00+00:00"' in html
    )
    assert 'class="chat-bubble-author"' not in html
    assert 'role="menuitemradio"' in html and 'data-chat-select="mode"' in html
    assert '<select id="chat-mode"' not in html
    assert 'href="/embed/cases?id=child"' in html
    assert "data-chat-focus-primary" not in html
    context_items = source["context"]["sections"][0]["items"]
    context_items.append(
        {
            "id": "focus",
            "label": "Next",
            "value": "Go to primary",
            "focus_primary": True,
        }
    )
    source["composer"]["primary"] = {
        "action_id": "prepare",
        "label": "Primary",
        "disabled": False,
    }
    template = env.get_template("components/layout/chat_workspace.html")
    with_primary = template.render(block=render_chat_workspace(source, "col-12"))
    assert "data-chat-primary" in with_primary
    assert "data-chat-focus-primary" in with_primary
    source["composer"]["primary"]["disabled"] = True
    assert "data-chat-focus-primary" not in template.render(
        block=render_chat_workspace(source, "col-12")
    )
    for invalid in (
        {"focus_primary": "true"},
        {"href": "/cases"},
        {"detail": "Details"},
    ):
        context_items[-1].update(invalid)
        with pytest.raises(ValueError, match="Invalid context composer focus"):
            render_chat_workspace(source, "col-12")
        context_items[-1].pop(next(iter(invalid)))
        context_items[-1]["focus_primary"] = True
    context_items.pop()
    for bad in ("https://foreign", "//foreign", "/../unsafe"):
        source["context"]["sections"][0]["items"][0]["href"] = bad
        with pytest.raises(ValueError):
            render_chat_workspace(source, "col-12")


@pytest.mark.parametrize(
    "key,value",
    [
        ("message_style", "javascript"),
        ("errors", {"invalid": "x" * 513}),
        ("errors", {"../escape": "unsafe"}),
    ],
)
def test_rejects_unbounded_optional_presentation(key, value):
    source = payload()
    source[key] = value
    with pytest.raises(ValueError):
        render_chat_workspace(source, "col-12")


def test_message_actions_details_and_navigation_render_safely():
    source = payload()
    source["messages"] = [
        {
            "id": "milestone",
            "sender": "host",
            "text": "Observed result",
            "details": "<script>private()</script>",
            "details_label": "Details",
            "links": [{"label": "Earlier", "href": "/cases?message_page=0"}],
            "actions": [
                {
                    "action_id": "investigate",
                    "label": label,
                    "disabled": disabled,
                    "args": {"source": "observed"},
                    "fields": [],
                    "navigate": {"href": "/cases", "param": "id", "result_key": "id"},
                }
                for label, disabled in (
                    ("First", False),
                    ("Second", False),
                    ("Third", True),
                )
            ],
        }
    ]
    block = render_chat_workspace(source, "col-12")
    resolve_chat_links(block, "/embed")
    message = block["messages"][0]
    assert len(message["actions"]) == 3
    assert message["links"][0]["href"] == "/embed/cases?message_page=0"
    assert message["actions"][0]["navigate"]["href"] == "/embed/cases"
    env = Environment(
        loader=FileSystemLoader("src/beeui_module/web/templates"),
        autoescape=select_autoescape(),
    )
    html = env.get_template("components/layout/chat_workspace.html").render(block=block)
    assert html.count("data-chat-message-action") == 3
    assert "<script>private()</script>" not in html
    assert "&lt;script&gt;private()&lt;/script&gt;" in html
    assert 'href="/embed/cases?message_page=0"' in html
    source["messages"][0]["actions"].append(source["messages"][0]["actions"][0])
    with pytest.raises(ValueError):
        render_chat_workspace(source, "col-12")


@pytest.mark.parametrize(
    "href", ["//foreign", "https://foreign", "/../escape", "javascript:alert(1)"]
)
def test_message_navigation_refuses_unsafe_links(href):
    source = payload()
    source["messages"] = [
        {
            "id": "message",
            "sender": "host",
            "text": "History",
            "links": [{"label": "History", "href": href}],
        }
    ]
    with pytest.raises(ValueError):
        render_chat_workspace(source, "col-12")
