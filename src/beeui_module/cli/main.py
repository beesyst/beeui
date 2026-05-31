from __future__ import annotations

import sys
from typing import Iterable

from beeui_module.cli.doctor import run_doctor
from beeui_module.cli.web import run_web
from beeui_module.core.paths import schema_path, settings_path
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version
from beeui_module.pages.config import load_beeui_config
from beeui_module.pages.router import prefixed_path


# Вывод маршрутов, доступных в текущей конфигурации приложения
def _print_routes() -> int:
    settings = load_settings(settings_path())
    ui_config = load_beeui_config(schema_path())
    route_prefix = settings["web"]["route_prefix"].strip().rstrip("/")
    prefix = route_prefix if route_prefix else ""

    print("Configured route surface:")
    for page in ui_config.pages:
        print(f"  GET {prefixed_path(prefix, page.path)}")
    print(f"  GET {prefix}/health")
    print(f"  GET {prefix}/static/...")
    return 0


# Обработка аргументов командной строки и вызывает соответствующие функции
def main(argv: Iterable[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        return run_doctor()

    command = arguments[0]
    if command == "doctor":
        return run_doctor()
    if command == "version":
        print(f"beeui {get_version()}")
        return 0
    if command == "routes":
        return _print_routes()
    if command == "web":
        return run_web(arguments[1:])

    print(
        "Unknown command: {command}. Available commands: doctor, version, routes, web".format(
            command=command,
        ),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
