from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from beeui_module.pages.links import prefix_internal_href, validate_internal_href

_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")


def _text(value: Any, limit: int = 256) -> str:
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError("Invalid workspace text")
    return value


def _id(value: Any) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("Invalid workspace identity")
    return value


def _items(value: Any, limit: int) -> list[dict]:
    if not isinstance(value, list) or len(value) > limit:
        raise ValueError("Invalid workspace collection")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError("Invalid workspace entry")
    return value


def _link(value: Any) -> str:
    href = validate_internal_href(value)
    if href is None or len(href) > 2048:
        raise ValueError("Invalid workspace link")
    return href


def normalize_messages(value: Any) -> list[dict]:
    messages = []
    seen = set()
    for item in _items(value, 100):
        identity = _text(item.get("id"), 128)
        if not identity or identity in seen:
            raise ValueError("Invalid message identity")
        seen.add(identity)
        sender = item.get("sender")
        if sender not in {"operator", "host", "assistant"}:
            raise ValueError("Invalid message sender")
        timestamp = _text(item.get("timestamp", ""), 40)
        if timestamp:
            datetime.fromisoformat(_text(timestamp, 40))
        messages.append(
            {
                "id": identity,
                "sender": sender,
                "name": _text(item.get("name", "")),
                "text": _text(item.get("text", ""), 4096),
                "timestamp": timestamp,
                "status": _text(item.get("status", ""), 80),
            }
        )
    if sum(len(item["text"]) for item in messages) > 32768:
        raise ValueError("Workspace message limit")
    return messages


def normalize_context(value: Any) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("Invalid workspace context")
    sections = []
    identities = set()
    total = 0
    count = 0
    for section in _items(value.get("sections"), 8):
        identity = _id(section.get("id"))
        if identity in identities:
            raise ValueError("Duplicate context section")
        identities.add(identity)
        items = []
        seen = set()
        title = _text(section.get("title"))
        total += len(title)
        for item in _items(section.get("items"), 64):
            key = _text(item.get("id"), 128)
            if not key or key in seen:
                raise ValueError("Invalid context identity")
            seen.add(key)
            entry = {
                "id": key,
                "label": _text(item.get("label", "")),
                "value": _text(item.get("value", ""), 4096),
                "detail": _text(item.get("detail", ""), 4096),
            }
            total += sum(len(entry[k]) for k in ("label", "value", "detail"))
            count += 1
            items.append(entry)
        sections.append({"id": identity, "title": title, "items": items})
    if total > 32768 or count > 128:
        raise ValueError("Workspace context limit")
    return {"title": _text(value.get("title", "")), "sections": sections}


def _composer(value: Any) -> dict:
    if not isinstance(value, dict):
        raise ValueError("Invalid composer")
    args = value.get("args", {})
    if not isinstance(args, dict) or len(args) > 10:
        raise ValueError("Invalid composer arguments")
    args = {_id(key): _text(item, 4096) for key, item in args.items()}
    fields = []
    names = set()
    for item in _items(value.get("fields", []), 8):
        name = _id(item.get("name"))
        kind = item.get("type")
        if (
            name in names
            or name in args
            or kind not in {"text", "url", "textarea", "select", "target", "segmented"}
        ):
            raise ValueError("Invalid composer field")
        names.add(name)
        maximum = item.get("max_length", 256)
        if type(maximum) is not int or not 1 <= maximum <= 4096:
            raise ValueError("Invalid composer field bound")
        field = {
            "name": name,
            "type": kind,
            "label": _text(item.get("label", name)),
            "value": _text(item.get("value", ""), maximum),
            "max_length": maximum,
            "required": item.get("required") is True,
            "readonly": item.get("readonly") is True,
            "placement": item.get("placement", "inline"),
        }
        if field["placement"] not in {"inline", "settings"}:
            raise ValueError("Invalid field placement")
        if kind in {"select", "segmented"}:
            field["options"] = [
                {
                    "value": _text(option.get("value")),
                    "label": _text(option.get("label")),
                }
                for option in _items(item.get("options"), 20)
            ]
            if not field["options"] or field["value"] not in {
                o["value"] for o in field["options"]
            }:
                raise ValueError("Invalid composer selection")
        protocols = item.get("protocols", [])
        if (
            not isinstance(protocols, list)
            or len(protocols) > 4
            or any(
                not isinstance(protocol, str)
                or re.fullmatch(r"[a-z][a-z0-9+.-]{0,15}", protocol) is None
                for protocol in protocols
            )
            or type(item.get("origin_only", False)) is not bool
        ):
            raise ValueError("Invalid target presentation constraint")
        field.update(
            protocols=protocols,
            origin_only=item.get("origin_only", False),
            invalid_message=_text(item.get("invalid_message", "")),
        )
        fields.append(field)
    navigate = value.get("navigate")
    if navigate is not None:
        if not isinstance(navigate, dict):
            raise ValueError("Invalid result navigation")
        navigate = {
            "href": _link(navigate.get("href")),
            "param": _id(navigate.get("param")),
            "result_key": _id(navigate.get("result_key")),
        }
    variant = value.get("variant", "form")
    if variant not in {"form", "compact"}:
        raise ValueError("Invalid composer variant")
    menu = value.get("menu")
    if menu is not None:
        if not isinstance(menu, dict):
            raise ValueError("Invalid composer menu")
        items = menu.get("items")
        if not isinstance(items, list) or not 1 <= len(items) <= 6:
            raise ValueError("Invalid disabled menu items")
        menu = {
            "label": _text(menu.get("label")),
            "items": [_text(item) for item in items],
        }
    return {
        "variant": variant,
        "submit_on_enter": value.get("submit_on_enter") is True,
        "menu": menu,
        "action_id": _id(value.get("action_id")),
        "args": args,
        "fields": fields,
        "disabled": value.get("disabled") is not False,
        "label": _text(value.get("label", "")),
        "hint": _text(value.get("hint", ""), 1024),
        "navigate": navigate,
        "settings_label": _text(value.get("settings_label", "")),
    }


def render_chat_workspace(raw: dict, width_class: str) -> dict:
    history = []
    seen = set()
    for item in _items(raw.get("history", []), 25):
        identity = _text(item.get("id"), 128)
        if not identity or identity in seen:
            raise ValueError("Invalid conversation identity")
        seen.add(identity)
        history.append(
            {
                "id": identity,
                "title": _text(item.get("title"), 4096),
                "href": _link(item.get("href")),
                "active": item.get("active") is True,
                "status": _text(item.get("status", ""), 80),
            }
        )
    refresh = raw.get("refresh")
    if refresh is not None:
        if not isinstance(refresh, dict):
            raise ValueError("Invalid workspace refresh")
        interval = refresh.get("interval_ms", 3000)
        attempts = refresh.get("max_attempts", 300)
        if type(interval) is not int or not 1000 <= interval <= 30000:
            raise ValueError("Invalid refresh interval")
        if type(attempts) is not int or not 1 <= attempts <= 300:
            raise ValueError("Invalid refresh bound")
        refresh = {
            "href": _link(refresh.get("href")),
            "interval_ms": interval,
            "max_attempts": attempts,
        }
    labels = raw.get("labels", {})
    if not isinstance(labels, dict):
        raise ValueError("Invalid workspace labels")
    search = raw.get("search")
    if search is not None:
        if not isinstance(search, dict):
            raise ValueError("Invalid workspace search")
        hidden = search.get("hidden", {})
        if not isinstance(hidden, dict) or len(hidden) > 4:
            raise ValueError("Invalid search arguments")
        search = {
            "href": _link(search.get("href")),
            "name": _id(search.get("name")),
            "value": _text(search.get("value", ""), 128),
            "hidden": {_id(k): _text(v, 128) for k, v in hidden.items()},
        }
    return {
        "type": "chat_workspace",
        "width_class": width_class,
        "id": _id(raw.get("id")),
        "title": _text(raw.get("title", "")),
        "state": _text(raw.get("state", ""), 80),
        "history": history,
        "messages": normalize_messages(raw.get("messages", [])),
        "empty_message": _text(raw.get("empty_message", ""), 1024),
        "history_notice": _text(raw.get("history_notice", ""), 1024),
        "labels": {
            key: _text(labels.get(key, ""))
            for key in (
                "history",
                "new",
                "search",
                "failed",
                "pending",
                "conversation",
                "context",
                "close",
            )
        },
        "new_href": _link(raw.get("new_href")),
        "search": search,
        "context": normalize_context(raw.get("context")),
        "composer": _composer(raw.get("composer")),
        "refresh": refresh,
    }


def resolve_chat_links(block: dict, prefix: str) -> None:
    for item in block["history"]:
        item["href"] = prefix_internal_href(prefix, item["href"])
    block["new_href"] = prefix_internal_href(prefix, block["new_href"])
    for value in (block["refresh"], block["search"], block["composer"]["navigate"]):
        if value:
            value["href"] = prefix_internal_href(prefix, value["href"])
