from __future__ import annotations

from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

from fastapi import Request

from beeui_module.pages.links import preserve_allowed_params

LocalizedText = str | dict[str, str]


def resolve_locale(
    request: Request,
    default: str,
    available: tuple[str, ...],
) -> str:
    lang = request.query_params.get("lang")
    if lang and lang in available:
        return lang
    return default


def resolve_localized_text(
    value: Any,
    selected_locale: str,
    default_locale: str,
) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if selected_locale in value:
            return str(value[selected_locale])
        return str(value.get(default_locale, ""))
    return str(value) if value is not None else ""


def validate_localized_text(
    value: Any,
    available_locales: tuple[str, ...],
    default_locale: str,
    field_name: str,
) -> None:
    if isinstance(value, str):
        if not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
        return

    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a string or a mapping")

    if not value:
        raise ValueError(f"{field_name} mapping must not be empty")

    for key, val in value.items():
        if key not in available_locales:
            raise ValueError(f"{field_name} contains unknown locale key: {key}")
        if not isinstance(val, str) or not val.strip():
            raise ValueError(f"{field_name}.{key} must be a non-empty string")

    if default_locale not in value:
        raise ValueError(
            f"{field_name} mapping must contain default locale key: {default_locale}"
        )


def build_lang_switch_href(
    request: Request,
    target_lang: str,
    route_prefix: str,
) -> str:
    current_params = preserve_allowed_params(dict(request.query_params))
    current_params["lang"] = target_lang
    qs = urlencode(sorted(current_params.items()))
    path = str(request.url.path)
    if route_prefix and path.startswith(route_prefix):
        path = path[len(route_prefix) :] or "/"
    parsed = urlsplit(path)
    result = urlunsplit(("", "", parsed.path, qs, ""))
    if route_prefix and not result.startswith(route_prefix):
        if result == "/":
            result = route_prefix or "/"
        else:
            result = f"{route_prefix}{result}"
    return result
