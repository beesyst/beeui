from __future__ import annotations

import sys
from typing import Iterable


# Ленивый import doctor-команды, чтобы version не тянул runtime stack.
def run_doctor() -> int:
    from beeui_module.cli.doctor import run_doctor as _run_doctor

    return _run_doctor()


# Ленивый import web-команды, потому что она подключает FastAPI/runtime stack.
def run_web(args: list[str]) -> int:
    from beeui_module.cli.web import run_web as _run_web

    return _run_web(args)


# Нормализация route_prefix для CLI routes output без импорта web stack.
def _normalize_route_prefix(route_prefix: str) -> str:
    cleaned = route_prefix.strip()
    if not cleaned:
        return ""
    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"
    return cleaned.rstrip("/")


# Вывод маршрутов, доступных в текущей конфигурации приложения
def _print_routes() -> int:
    from beeui_module.core.paths import schema_path, settings_path
    from beeui_module.core.settings import load_settings
    from beeui_module.pages.config import load_beeui_config
    from beeui_module.pages.router import prefixed_path

    settings = load_settings(settings_path())
    ui_config = load_beeui_config(schema_path())
    prefix = _normalize_route_prefix(settings["web"]["route_prefix"])

    print("Configured route surface:")
    for page in ui_config.pages:
        print(f"  GET {prefixed_path(prefix, page.path)}")
    print(f"  GET {prefixed_path(prefix, '/components')}")
    print(f"  GET {prefixed_path(prefix, '/components/interface')}")
    print(f"  GET {prefixed_path(prefix, '/components/forms')}")
    print(f"  GET {prefixed_path(prefix, '/components/layout')}")
    print(f"  GET {prefixed_path(prefix, '/components/extra')}")
    print(f"  GET {prefixed_path(prefix, '/components/plugins')}")
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
        from beeui_module.core.version import get_version

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
