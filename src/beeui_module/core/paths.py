from __future__ import annotations

from pathlib import Path


def project_root(start: Path | str | None = None) -> Path:
    current = Path(start or __file__).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate

    raise FileNotFoundError(
        "pyproject.toml was not found while resolving the BeeUI root"
    )


PROJECT_ROOT = project_root()
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"
STORAGE_DIR = PROJECT_ROOT / "storage"


def config_directory(root: Path | str | None = None) -> Path:
    return project_root(root) / "config"


def settings_path(root: Path | str | None = None) -> Path:
    return config_directory(root) / "settings.yml"


def schema_path(root: Path | str | None = None) -> Path:
    return config_directory(root) / "schema.yml"


def logs_directory(root: Path | str | None = None) -> Path:
    return project_root(root) / "logs"


def log_file_path(
    root: Path | str | None = None,
    log_file: str = "logs/app.log",
) -> Path:
    resolved_root = project_root(root).resolve()
    raw_path = Path(log_file)

    if raw_path.is_absolute():
        raise ValueError("logging.file must be a relative path")

    resolved_path = (resolved_root / raw_path).resolve()
    if resolved_root not in (resolved_path, *resolved_path.parents):
        raise ValueError("logging.file must stay under project root")

    return resolved_path
