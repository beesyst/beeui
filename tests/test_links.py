from __future__ import annotations

from beeui_module.pages.links import (
    add_preserved_params_to_href,
    is_safe_internal_href,
    preserve_allowed_params,
)


def test_preserve_allowed_params_filters_unknown() -> None:
    params = {"lang": "ru", "period": "24h", "run_id": "r1", "secret": "bad"}
    result = preserve_allowed_params(params)
    assert result == {"lang": "ru", "period": "24h", "run_id": "r1"}
    assert "secret" not in result


def test_preserve_allowed_params_filters_empty_values() -> None:
    params = {"lang": "ru", "period": "", "run_id": "   "}
    assert preserve_allowed_params(params) == {"lang": "ru"}


def test_preserve_allowed_params_empty() -> None:
    assert preserve_allowed_params({}) == {}
    assert preserve_allowed_params(None) == {}


def test_preserve_allowed_params_custom_allowlist() -> None:
    params = {"lang": "ru", "foo": "bar"}
    result = preserve_allowed_params(params, frozenset({"foo"}))
    assert result == {"foo": "bar"}
    assert "lang" not in result


def test_add_preserved_params_to_href_no_params() -> None:
    assert add_preserved_params_to_href("/rop?tab=overview", {}) == "/rop?tab=overview"


def test_add_preserved_params_to_href_adds_lang() -> None:
    result = add_preserved_params_to_href("/rop?tab=overview", {"lang": "ru"})
    assert "lang=ru" in result
    assert "tab=overview" in result


def test_add_preserved_params_to_href_merges_existing() -> None:
    result = add_preserved_params_to_href("/rop?lang=en", {"lang": "ru"})
    assert "lang=ru" in result  # overrides existing


def test_add_preserved_params_to_href_preserves_period_and_run_id() -> None:
    result = add_preserved_params_to_href(
        "/rop?tab=threads",
        {"lang": "ru", "period": "7d", "run_id": "run_001"},
    )
    assert "lang=ru" in result
    assert "period=7d" in result
    assert "run_id=run_001" in result
    assert "tab=threads" in result


def test_is_safe_internal_href_accepts_simple_path() -> None:
    assert is_safe_internal_href("/rop")
    assert is_safe_internal_href("/rop?tab=overview")
    assert is_safe_internal_href("/rop?lang=ru&tab=overview")


def test_is_safe_internal_href_rejects_external() -> None:
    assert not is_safe_internal_href("https://example.com")
    assert not is_safe_internal_href("http://evil.com")
    assert not is_safe_internal_href("//evil.com")
    assert not is_safe_internal_href("javascript:alert(1)")


def test_is_safe_internal_href_rejects_traversal() -> None:
    assert not is_safe_internal_href("/../etc")
    assert not is_safe_internal_href("/runs/../../../etc")
