from __future__ import annotations

import sys
from typing import Iterable

from beeui_module.cli.doctor import run_doctor
from beeui_module.cli.serve import run_serve
from beeui_module.core.version import get_version


# Печать информации о маршрутах, которые будут доступны в будущих итерациях
def _print_routes() -> int:
    print("Iteration 0 route surface: none")
    print("Planned web routes:")
    print("  GET /health")
    print("  GET /version")
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
        return run_serve()

    print(
        "Unknown command: {command}. Available commands: doctor, version, routes, serve".format(
            command=command,
        ),
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
