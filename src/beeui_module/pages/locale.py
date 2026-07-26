from __future__ import annotations

from typing import Any
from urllib.parse import urlencode, urlsplit, urlunsplit

from fastapi import Request

from beeui_module.pages.links import preserve_allowed_params

LocalizedText = str | dict[str, str]

_BEEUI_TRANSLATIONS: dict[str, dict[str, str]] = {
    "filter.columns": {"en": "Columns", "ru": "Колонки"},
    "filter.any": {"en": "Any", "ru": "Любой"},
    "filter.apply": {"en": "Apply", "ru": "Применить"},
    "detail.show_text": {"en": "Show text", "ru": "Показать текст"},
    "detail.unavailable": {"en": "Unavailable", "ru": "Недоступно"},
    "chart.title": {"en": "Chart", "ru": "График"},
    "chart.unit": {"en": "Unit:", "ru": "Ед.:"},
    "chart.empty": {"en": "No data to display", "ru": "Нет данных для отображения"},
    "chart.unavailable": {"en": "Chart unavailable", "ru": "График недоступен"},
    "chart.error": {"en": "Chart render error", "ru": "Ошибка рендеринга графика"},
    "auth.disabled": {"en": "Auth is disabled in local/dev mode", "ru": "Аутентификация отключена в локальном режиме"},
    "auth.invalid_form": {"en": "Invalid form data", "ru": "Неверные данные формы"},
    "auth.required": {"en": "User ID and token are required", "ru": "Необходимы ID пользователя и токен"},
    "theme.label": {"en": "Theme", "ru": "Тема"},
    "theme.system": {"en": "System", "ru": "Системная"},
    "theme.light": {"en": "Light", "ru": "Светлая"},
    "theme.dark": {"en": "Dark", "ru": "Тёмная"},
    "theme.system_aria": {"en": "System theme", "ru": "Системная тема"},
    "theme.light_aria": {"en": "Light theme", "ru": "Светлая тема"},
    "theme.dark_aria": {"en": "Dark theme", "ru": "Тёмная тема"},
}


def translate(key: str, locale: str, default_locale: str = "en") -> str:
    messages = _BEEUI_TRANSLATIONS.get(key)
    if messages is None:
        return key
    return messages.get(locale) or messages.get(default_locale) or messages["en"]


def resolve_locale(
    request: Request,
    default: str,
    available: tuple[str, ...],
) -> str:
    lang = request.query_params.get("lang")
    if lang and lang in available:
        return lang
    lang = request.cookies.get("beeui_lang")
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
