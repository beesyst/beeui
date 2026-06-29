from __future__ import annotations

from pathlib import Path

from beeui_module.core.paths import (
    CONFIG_DIR,
    LOGS_DIR,
    PROJECT_ROOT,
    STORAGE_DIR,
    log_file_path,
    project_root,
    schema_path,
    settings_path,
)


def test_project_root_is_resolved_from_pyproject() -> None:
    resolved_root = project_root(Path(__file__))

    assert (resolved_root / "pyproject.toml").is_file()
    assert resolved_root.name == "beeui"
    assert resolved_root == PROJECT_ROOT


def test_log_and_settings_paths_are_under_project_root() -> None:
    resolved_root = project_root(Path(__file__))

    assert log_file_path(resolved_root) == resolved_root / "logs" / "app.log"
    assert settings_path(resolved_root) == resolved_root / "config" / "settings.yml"
    assert schema_path(resolved_root) == resolved_root / "config" / "schema.yml"


def test_path_constants_point_to_project_subdirectories() -> None:
    assert CONFIG_DIR == project_root(Path(__file__)) / "config"
    assert LOGS_DIR == project_root(Path(__file__)) / "logs"
    assert STORAGE_DIR == project_root(Path(__file__)) / "storage"
