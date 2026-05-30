from __future__ import annotations

from pathlib import Path

from beeui_module.core.log import configure_logging
from beeui_module.core.paths import log_file_path, project_root, settings_path


# Запуск чека окружения и конфигурации проекта
def run_doctor(root: Path | str | None = None) -> int:
    resolved_root = project_root(root)
    config_path = settings_path(resolved_root)

    if not config_path.is_file():
        raise FileNotFoundError(f"Settings config is missing: {config_path}")

    from beeui_module.core.settings import load_settings

    settings = load_settings(config_path)
    logging_config = settings["logging"]

    logger = configure_logging(
        root=resolved_root,
        level=logging_config["level"],
        utc=logging_config["utc"],
        clear_logs=logging_config["clear_logs"],
        log_file=logging_config["file"],
    )
    logger.info("beeui doctor: ok")
    logger.info("root=%s", resolved_root)
    logger.info("config=%s", config_path)
    logger.info("log=%s", log_file_path(resolved_root, logging_config["file"]))
    return 0
