from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Модели данных для конфигурации UI, навигации и страниц BeeUI
@dataclass(frozen=True)
class BeeUiNavigationItem:
    title: str
    path: str
    icon: str | None = None


# Модель страницы BeeUI, содержащая идентификатор, путь, заголовок, необязательный подзаголовок и блоки контента
@dataclass(frozen=True)
class BeeUiPage:
    page_id: str
    path: str
    title: str
    subtitle: str | None
    blocks: list[Any]


# Модель конфигурации BeeUI, включающая заголовок приложения, идентификатор продукта, навигацию и страницы
@dataclass(frozen=True)
class BeeUiConfig:
    app_title: str
    product: str
    navigation: list[BeeUiNavigationItem]
    pages: list[BeeUiPage]
