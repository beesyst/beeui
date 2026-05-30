from __future__ import annotations

import sys
from typing import Iterable

from beeui_module.cli.doctor import run_doctor
from beeui_module.cli.serve import run_serve
from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.core.version import get_version


# Вывод маршрутов, доступных в текущей конфигурации приложения
def _print_routes() -> int:
    settings = load_settings(settings_path())
    route_prefix = settings["web"]["route_prefix"].strip().rstrip("/")
    prefix = route_prefix if route_prefix else ""

    print("Iteration 1 route surface:")
    print(f"  GET {prefix or '/'}")
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
    if command == "serve":
        return run_serve(arguments[1:])

    print(
        "Unknown command: {command}. Available commands: doctor, version, routes, serve".format(
            command=command,
        ),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
