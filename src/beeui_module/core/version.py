from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


# Получение версии пакета beeui, возвращает "0.0.0+local" если пакет не найден
def get_version() -> str:
    try:
        return version("beeui")
    except PackageNotFoundError:
        return "0.0.0+local"
