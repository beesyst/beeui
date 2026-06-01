from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Модель конфигурации темы BeeUI
@dataclass(frozen=True)
class ThemeConfig:
    mode: str
    primary: str
    base: str
    font: str
    radius: int
    density: str


# Модель конфигурации сайдбара, включающая вариант и состояние свернутости
@dataclass(frozen=True)
class SidebarConfig:
    variant: str
    collapsed: bool


# Модель конфигурации верхнего navbar
@dataclass(frozen=True)
class NavbarConfig:
    enabled: bool
    variant: str
    sticky: bool


# Модель конфигурации layout shell
@dataclass(frozen=True)
class LayoutConfig:
    type: str
    container: str
    sidebar: SidebarConfig
    navbar: NavbarConfig


# Модель навигационного элемента, включающая заголовок, путь, иконку, состояние отключения и вложенные элементы
@dataclass(frozen=True)
class BeeUiNavigationItem:
    title: str
    path: str | None = None
    icon: str | None = None
    disabled: bool = False
    children: list["BeeUiNavigationItem"] = field(default_factory=list)


# Модель страницы BeeUI, содержащая идентификатор, путь, заголовок, необязательный подзаголовок и блоки контента
@dataclass(frozen=True)
class BeeUiPage:
    page_id: str
    path: str
    title: str
    subtitle: str | None
    blocks: list[Any]


# Модель конфигурации BeeUI, включающая приложение, тему, layout, навигацию и страницы
@dataclass(frozen=True)
class BeeUiConfig:
    app_title: str
    product: str
    logo_text: str
    theme: ThemeConfig
    layout: LayoutConfig
    navigation: list[BeeUiNavigationItem]
    pages: list[BeeUiPage]
