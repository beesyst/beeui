from pathlib import Path

from beeui_module.pages.icons import is_safe_icon_name, safe_icon_name


def test_canonical_tabler_icon_names_are_safe() -> None:
    for name in (
        "dashboard",
        "users",
        "activity",
        "apps",
        "dashboard",
        "stack",
        "database",
        "ban",
    ):
        assert is_safe_icon_name(name)
        assert safe_icon_name(name) == name


def test_unsafe_icon_names_are_omitted() -> None:
    for value in ("", "Dashboard", "bad_icon", "<svg>", "icon onload=alert(1)"):
        assert not is_safe_icon_name(value)
        assert safe_icon_name(value) is None


def test_webfont_assets_are_packaged() -> None:
    root = Path(__file__).parents[1]
    package_data = (root / "pyproject.toml").read_text(encoding="utf-8")
    stylesheet = (
        root / "src/beeui_module/web/static/vendor/tabler-icons/tabler-icons.min.css"
    ).read_text(encoding="utf-8")

    assert '"static/vendor/tabler-icons/**/*",' in package_data
    assert (root / "src/beeui_module/web/static/vendor/tabler-icons/LICENSE").is_file()
    assert (root / "src/beeui_module/web/static/vendor/tabler-icons/VERSION").is_file()
    for name in ("dashboard", "users", "activity", "apps", "stack", "database", "ban"):
        assert f".ti-{name}:before" in stylesheet
