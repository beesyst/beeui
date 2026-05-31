from __future__ import annotations

from pathlib import Path

from beeui_module.pages.config import load_beeui_config

_VALID_CONFIG = """app:
  title: BeeUI Demo
  product: demo

navigation:
  - title: Dashboard
    path: /
    icon: dashboard
  - title: Runs
    path: /runs
    icon: list

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


# Тест: запись временного YAML-конфига
def _write_config(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "schema.yml"
    config_path.write_text(content, encoding="utf-8")
    return config_path


# Тест: чек, что load_beeui_config успешно загружает валидный конфиг и парсит его в ожидаемую структуру
def test_load_beeui_config_valid_payload() -> None:
    config = load_beeui_config(Path("config/schema.yml"))

    assert config.app_title == "BeeUI Demo"
    assert config.product == "demo"
    assert [page.path for page in config.pages] == ["/", "/runs"]


# Тест: чек, что load_beeui_config выбрасывает исключение при отсутствии обязательного поля app.title
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


# Тест: duplicate page id вызывает fail-fast ошибку
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


# Тест: duplicate page path вызывает fail-fast ошибку
def test_load_beeui_config_fails_on_duplicate_page_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace("path: /runs", "path: /"),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "Duplicate page path: /"
    else:
        raise AssertionError("load_beeui_config must fail on duplicate page path")


# Тест: чек, что load_beeui_config выбрасывает исключение при навигационном элементе с неизвестным путем
def test_load_beeui_config_fails_on_unknown_navigation_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace("path: /runs", "path: /missing", 1),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "navigation path must match a declared page path: /missing"
    else:
        raise AssertionError("load_beeui_config must fail on unknown navigation path")


# Тест: чек, что load_beeui_config выбрасывает исключение при небезопасном пути страницы
def test_load_beeui_config_rejects_unsafe_page_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "  - id: runs\n    path: /runs",
            "  - id: runs\n    path: /../runs",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[1].path must be a safe path"
    else:
        raise AssertionError("load_beeui_config must reject unsafe page path")


# Тест: отсутствие blocks у страницы вызывает fail-fast ошибку
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


# Тест: чек, что load_beeui_config выбрасывает исключение при использовании зарезервированного пути /health
def test_load_beeui_config_rejects_reserved_health_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "  - id: runs\n    path: /runs",
            "  - id: runs\n    path: /health",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /health path")


# Тест: чек, что load_beeui_config выбрасывает исключение при использовании зарезервированного пути /static
def test_load_beeui_config_rejects_reserved_static_path(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "  - id: runs\n    path: /runs",
            "  - id: runs\n    path: /static",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /static path")


# Тест: чек, что load_beeui_config выбрасывает исключение при использовании зарезервированного префикса /static/ в пути страницы
def test_load_beeui_config_rejects_reserved_static_prefix(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _VALID_CONFIG.replace(
            "  - id: runs\n    path: /runs",
            "  - id: runs\n    path: /static/css/beeui.css",
        ),
    )

    try:
        load_beeui_config(config_path)
    except ValueError as exc:
        assert str(exc) == "pages[1].path uses a reserved path"
    else:
        raise AssertionError("load_beeui_config must reject reserved /static/... path")
