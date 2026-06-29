from __future__ import annotations

from beeui_module.pages.locale import (
    resolve_localized_text,
    validate_localized_text,
)

_AVAILABLE = ("en", "ru")
_DEFAULT = "en"


def test_resolve_localized_text_plain_string() -> None:
    assert resolve_localized_text("Overview", "en", "en") == "Overview"
    assert resolve_localized_text("Overview", "ru", "en") == "Overview"


def test_resolve_localized_text_dict_selected_locale() -> None:
    value = {"en": "Overview", "ru": "Обзор"}
    assert resolve_localized_text(value, "en", "en") == "Overview"
    assert resolve_localized_text(value, "ru", "en") == "Обзор"


def test_resolve_localized_text_dict_falls_back_to_default() -> None:
    value = {"en": "Overview", "ru": "Обзор"}
    assert resolve_localized_text(value, "fr", "en") == "Overview"


def test_resolve_localized_text_dict_missing_both_returns_empty() -> None:
    value = {"ru": "Обзор"}
    assert resolve_localized_text(value, "fr", "en") == ""


def test_resolve_localized_text_none_returns_empty() -> None:
    assert resolve_localized_text(None, "en", "en") == ""


def test_validate_localized_text_plain_string() -> None:
    validate_localized_text("Hello", _AVAILABLE, _DEFAULT, "test")
    # No exception means pass


def test_validate_localized_text_valid_dict() -> None:
    validate_localized_text(
        {"en": "Overview", "ru": "Обзор"},
        _AVAILABLE,
        _DEFAULT,
        "test",
    )


def test_validate_localized_text_unknown_locale_key_fails() -> None:
    try:
        validate_localized_text(
            {"en": "OK", "fr": "Bonjour"},
            _AVAILABLE,
            _DEFAULT,
            "test",
        )
    except ValueError as exc:
        assert "contains unknown locale key" in str(exc)
    else:
        raise AssertionError("must fail on unknown locale key")


def test_validate_localized_text_missing_default_fails() -> None:
    try:
        validate_localized_text(
            {"ru": "Привет"},
            _AVAILABLE,
            _DEFAULT,
            "test",
        )
    except ValueError as exc:
        assert "must contain default locale key" in str(exc)
    else:
        raise AssertionError("must fail on missing default locale")


def test_validate_localized_text_empty_mapping_fails() -> None:
    try:
        validate_localized_text({}, _AVAILABLE, _DEFAULT, "test")
    except ValueError as exc:
        assert "must not be empty" in str(exc)
    else:
        raise AssertionError("must fail on empty mapping")


def test_validate_localized_text_non_string_value_fails() -> None:
    try:
        validate_localized_text(
            {"en": 42, "ru": "Привет"},
            _AVAILABLE,
            _DEFAULT,
            "test",
        )
    except ValueError as exc:
        assert "must be a non-empty string" in str(exc)
    else:
        raise AssertionError("must fail on non-string value")


def test_validate_localized_text_invalid_type_fails() -> None:
    try:
        validate_localized_text(42, _AVAILABLE, _DEFAULT, "test")
    except ValueError as exc:
        assert "must be a string or a mapping" in str(exc)
    else:
        raise AssertionError("must fail on invalid type")


def test_build_lang_switch_href_preserves_only_allowlisted_params() -> None:
    from fastapi import Request

    from beeui_module.pages.locale import build_lang_switch_href

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/rop",
        "query_string": b"lang=en&secret=bad&period=24h&evil=yes",
        "headers": [],
        "scheme": "http",
        "server": ("test", 80),
    }
    request = Request(scope)
    result = build_lang_switch_href(request, "ru", "")
    assert "lang=ru" in result
    assert "period=24h" in result
    assert "secret" not in result
    assert "evil" not in result


def test_build_lang_switch_href_ignores_unknown_params() -> None:
    from fastapi import Request

    from beeui_module.pages.locale import build_lang_switch_href

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/rop",
        "query_string": b"tab=overview&utm_source=bad",
        "headers": [],
        "scheme": "http",
        "server": ("test", 80),
    }
    request = Request(scope)
    result = build_lang_switch_href(request, "ru", "")
    assert "lang=ru" in result
    assert "tab=overview" not in result
    assert "utm_source" not in result
