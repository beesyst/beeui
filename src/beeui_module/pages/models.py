from __future__ import annotations

from dataclasses import dataclass, field

from beeui_module.blocks.models import BlockDefinition, BlockPlacement


# Настройки темы, прошедшие schema validation
@dataclass(frozen=True)
class ThemeConfig:
    mode: str
    primary: str
    base: str
    font: str
    radius: int
    density: str


# Настройки боковой навигации
@dataclass(frozen=True)
class SidebarConfig:
    variant: str
    collapsed: bool


# Настройки верхнего navbar
@dataclass(frozen=True)
class NavbarConfig:
    enabled: bool
    variant: str
    sticky: bool


# Общая конфигурация layout shell
@dataclass(frozen=True)
class LayoutConfig:
    type: str
    container: str
    sidebar: SidebarConfig
    navbar: NavbarConfig


# Элемент навигации: либо ссылка на страницу, либо группа children
@dataclass(frozen=True)
class BeeUiNavigationItem:
    title: str
    path: str | None = None
    icon: str | None = None
    disabled: bool = False
    children: list["BeeUiNavigationItem"] = field(default_factory=list)


# Страница BeeUI с валидированными block placements
@dataclass(frozen=True)
class BeeUiPage:
    page_id: str
    path: str
    title: str
    subtitle: str | None
    blocks: list[BlockPlacement]


# Полная read-only конфигурация BeeUI, собранная из schema.yml
@dataclass(frozen=True)
class BeeUiConfig:
    app_title: str
    product: str
    logo_text: str
    theme: ThemeConfig
    layout: LayoutConfig
    navigation: list[BeeUiNavigationItem]
    blocks: dict[str, BlockDefinition]
    pages: list[BeeUiPage]
