from __future__ import annotations

from pathlib import Path

from beeui_module.pages.config import load_beeui_config

_VALID_CONFIG = """app:
  title: BeeUI Demo
  product: demo
  logo_text: BeeUI
  theme:
    mode: dark
    primary: blue
    base: gray
    font: sans-serif
    radius: 1
    density: default
  layout:
    type: vertical
    container: xl
    sidebar:
      variant: dark
      collapsed: false
    navbar:
      enabled: true
      variant: default
      sticky: false

navigation:
  - title: Workspace
    children:
      - title: Dashboard
        path: /
        icon: dashboard
      - title: Runs
        path: /runs
        icon: list
      - title: Reports
        disabled: true

pages:
  - id: dashboard
    path: /
    title: Dashboard
    subtitle: Demo operator dashboard
    blocks: []
  - id: runs
    path: /runs
    title: Runs
    subtitle: Placeholder page for future run overview
    blocks: []
"""


# Конфигурация с потенциально опасными значениями для проверки экранирования
def _write_config(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "schema.yml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


# Тест: загрузка валидного конфига и проверка его полей
def test_load_beeui_config_valid_payload() -> None:
    config = load_beeui_config(Path("config/schema.yml"))

    assert config.app_title == "BeeUI Demo"
    assert config.product == "demo"
    assert config.logo_text == "BeeUI"
    assert config.theme.mode == "dark"
    assert config.layout.container == "xl"
    assert [page.path for page in config.pages] == ["/", "/runs"]


# Тест: чек, что строки, предоставленные в конфиге, экранируются для предотвращения XSS
def test_load_beeui_config_fails_on_missing_app_title(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace("  title: BeeUI Demo\n", ""),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "app.title must be a non-empty string"
    else:
        raise AssertionError("load_beeui_config must fail on missing app.title")


def test_load_beeui_config_fails_on_missing_logo_text(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace("  logo_text: BeeUI\n", ""),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "app.logo_text must be a non-empty string"
    else:
        raise AssertionError("load_beeui_config must fail on missing app.logo_text")


# Тест: чек, что строки, предоставленные в конфиге, экранируются для предотвращения XSS
def test_load_beeui_config_rejects_invalid_theme_and_layout_values(
    tmp_path: Path,
) -> None:
    invalid_cases = [
        (
            _VALID_CONFIG.replace("    primary: blue\n", ""),
            "app.theme.primary must be a non-empty string",
        ),
        (
            _VALID_CONFIG.replace("mode: dark", "mode: neon"),
            "app.theme.mode must be one of ['auto', 'dark', 'light']",
        ),
        (
            _VALID_CONFIG.replace("primary: blue", "primary: purple"),
            "app.theme.primary must be one of ['azure', 'blue', 'cyan', 'green', 'indigo', 'lime', 'orange', 'pink', 'red', 'teal', 'yellow']",
        ),
        (
            _VALID_CONFIG.replace("base: gray", "base: ivory"),
            "app.theme.base must be one of ['gray', 'neutral', 'slate', 'stone', 'zinc']",
        ),
        (
            _VALID_CONFIG.replace("font: sans-serif", "font: comic-sans"),
            "app.theme.font must be one of ['monospace', 'sans-serif', 'serif']",
        ),
        (
            _VALID_CONFIG.replace("radius: 1", "radius: 7"),
            "app.theme.radius must be one of [0, 1, 2]",
        ),
        (
            _VALID_CONFIG.replace("density: default", "density: spacious"),
            "app.theme.density must be one of ['comfortable', 'compact', 'default']",
        ),
        (
            _VALID_CONFIG.replace("type: vertical", "type: horizontal"),
            "app.layout.type must be one of ['vertical']",
        ),
        (
            _VALID_CONFIG.replace("container: xl", "container: lg"),
            "app.layout.container must be one of ['fluid', 'xl']",
        ),
        (
            _VALID_CONFIG.replace("variant: dark", "variant: compact", 1),
            "app.layout.sidebar.variant must be one of ['dark', 'default']",
        ),
        (
            _VALID_CONFIG.replace("collapsed: false", "collapsed: maybe"),
            "app.layout.sidebar.collapsed must be a boolean",
        ),
        (
            _VALID_CONFIG.replace("enabled: true", "enabled: maybe"),
            "app.layout.navbar.enabled must be a boolean",
        ),
        (
            _VALID_CONFIG.replace("variant: default", "variant: floating"),
            "app.layout.navbar.variant must be one of ['dark', 'default']",
        ),
        (
            _VALID_CONFIG.replace("sticky: false", "sticky: maybe"),
            "app.layout.navbar.sticky must be a boolean",
        ),
    ]

    for index, (content, expected_message) in enumerate(invalid_cases):
        config_path = _write_config(tmp_path, content)

        try:
            load_beeui_config(config_path)
        except ValueError as exc:
            assert str(exc) == expected_message, index
        else:
            raise AssertionError(f"load_beeui_config must fail on case {index}")


# Тест: чек, что строки, предоставленные в конфиге, экранируются для предотвращения XSS
def test_load_beeui_config_rejects_arbitrary_css_js_html_keys(tmp_path: Path) -> None:
    forbidden_keys = [
        "custom_css",
        "css",
        "style",
        "custom_js",
        "script",
        "javascript",
        "html",
    ]

    for forbidden_key in forbidden_keys:
        config_path = _write_config(
            tmp_path,
            _VALID_CONFIG.replace(
                "  theme:\n",
                f"  {forbidden_key}: injected\n  theme:\n",
                1,
            ),
        )

        try:
            load_beeui_config(config_path)
        except ValueError as exc:
            assert str(exc) == f"app contains unsupported keys: {forbidden_key}"
        else:
            raise AssertionError(
                f"load_beeui_config must reject arbitrary key {forbidden_key}"
            )


# Тест: загрузка конфига с дублирующимися id страниц вызывает ошибку
def test_load_beeui_config_fails_on_duplicate_page_id(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace("id: runs", "id: dashboard"),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "Duplicate page id: dashboard"
    else:
        raise AssertionError("load_beeui_config must fail on duplicate page id")


# Тест: загрузка конфига с дублирующимися путями страниц вызывает ошибку
def test_load_beeui_config_fails_on_duplicate_page_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "  - id: runs\n    path: /runs\n",
            "  - id: runs\n    path: /\n",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "Duplicate page path: /"
    else:
        raise AssertionError("load_beeui_config must fail on duplicate page path")


# Тест: загрузка конфига с дублирующимися путями в навигации вызывает ошибку
def test_load_beeui_config_fails_on_duplicate_nested_navigation_path(
    tmp_path: Path,
) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "        path: /runs\n        icon: list\n",
            "        path: /\n        icon: list\n",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "Duplicate navigation path: /"
    else:
        raise AssertionError("load_beeui_config must fail on duplicate navigation path")


# Тест: загрузка конфига с навигационным путем, не соответствующим ни одной странице, вызывает ошибку
def test_load_beeui_config_fails_on_unknown_navigation_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "        path: /runs\n        icon: list\n",
            "        path: /missing\n        icon: list\n",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation path must match a declared page path: /missing"
    else:
        raise AssertionError("load_beeui_config must fail on unknown navigation path")


# Тест: загрузка конфига с навигационным путем, начинающимся с внешнего URL, вызывает ошибку
def test_load_beeui_config_rejects_external_navigation_path(tmp_path: Path) -> None:
    invalid_links = [
        ("https://example.com", "navigation[0].children[1].path must start with '/'"),
        ("http://example.com", "navigation[0].children[1].path must start with '/'"),
        ("//example.com", "navigation[0].children[1].path must be a safe path"),
        (
            "mailto:test@example.com",
            "navigation[0].children[1].path must start with '/'",
        ),
        ("javascript:alert(1)", "navigation[0].children[1].path must start with '/'"),
    ]

    for raw_path, expected_message in invalid_links:
        config_path = _write_config(
            tmp_path,
            _VALID_CONFIG.replace(
                "        path: /runs\n        icon: list\n",
                f"        path: {raw_path}\n        icon: list\n",
            ),
        )

        try:
            load_beeui_config(config_path)
        except ValueError as exc:
            assert str(exc) == expected_message
        else:
            raise AssertionError(
                f"load_beeui_config must reject external navigation link {raw_path}"
            )


def test_load_beeui_config_fails_on_missing_blocks(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace("    blocks: []\n", "", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[0].blocks must be a list"
    else:
        raise AssertionError("load_beeui_config must fail when blocks key is missing")


# Тест: загрузка конфига с навигационным путем, совпадающим с зарезервированными путями, вызывает ошибку
def test_load_beeui_config_rejects_reserved_health_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "        path: /runs\n        icon: list\n",
            "        path: /health\n        icon: list\n",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /health path")


# Тест: загрузка конфига с навигационным путем, совпадающим с зарезервированными путями, вызывает ошибку
def test_load_beeui_config_rejects_reserved_static_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "        path: /runs\n        icon: list\n",
            "        path: /static\n        icon: list\n",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /static path")


# Тест: загрузка конфига с навигационным путем, начинающимся с зарезервированного префикса /static/, вызывает ошибку
def test_load_beeui_config_rejects_reserved_static_prefix(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "        path: /runs\n        icon: list\n",
            "        path: /static/css/beeui.css\n        icon: list\n",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation[0].children[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /static/... path")
