from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import uvicorn

from beeui_module.core.log import configure_logging
from beeui_module.core.paths import project_root, settings_path
from beeui_module.core.settings import load_settings
from beeui_module.web.app import create_beeui_app


# Парсинг аргументов командной строки для команды web
def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="beeui web")
    parser.add_argument("--host", type=str, default=None)
    parser.add_argument("--port", type=int, default=None)
    return parser.parse_args(list(argv or []))


# Запуск веб-сервера с конфигурацией из настроек и аргументов командной строки
def run_web(argv: Iterable[str] | None = None, root: Path | str | None = None) -> int:
    args = _parse_args(argv)

    resolved_root = project_root(root)
    cfg_path = settings_path(resolved_root)
    settings = load_settings(cfg_path)

    logging_cfg = settings["logging"]
    logger = configure_logging(
        root=resolved_root,
        level=logging_cfg["level"],
        utc=logging_cfg["utc"],
        clear_logs=logging_cfg["clear_logs"],
        log_file=logging_cfg["file"],
    )

    app = create_beeui_app(settings=settings)

    web_cfg = settings["web"]
    host = args.host if args.host is not None else web_cfg["host"]
    port = args.port if args.port is not None else web_cfg["port"]

    logger.info("beeui web: starting on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level=logging_cfg["level"].lower())
    return 0
