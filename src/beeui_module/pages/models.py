from __future__ import annotations

from dataclasses import dataclass, field

from beeui_module.blocks.models import BlockDefinition, BlockPlacement
from beeui_module.data.models import DataSourceDefinition


# Локаль: default locale и список доступных локалей
@dataclass(frozen=True)
class LocaleConfig:
    default: str = "en"
    available: tuple[str, ...] = ("en",)


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


# Оформления для Tabs и Accordion
TABS_VARIANTS = frozenset(
    {"default", "reverse", "fill", "icons", "fill_icons", "dropdown"}
)
ACCORDION_VARIANTS = frozenset(
    {"default", "flush", "tabs", "inverted", "inverted_plus", "icons"}
)
TABS_VARIANT_NUMERIC: dict[int, str] = {
    1: "default",
    2: "reverse",
    3: "icons",
    4: "dropdown",
    5: "fill",
    6: "fill_icons",
}
ACCORDION_VARIANT_NUMERIC: dict[int, str] = {
    1: "default",
    2: "flush",
    3: "tabs",
    4: "inverted",
    5: "inverted_plus",
    6: "icons",
}


# Нормализация вариантов оформления для Tabs и Accordion, поддерживающая как строковые, так и числовые варианты
def normalize_tabs_variant(variant: str | int) -> str:
    if isinstance(variant, int):
        if variant not in TABS_VARIANT_NUMERIC:
            raise ValueError(f"Invalid tabs variant: {variant}")
        return TABS_VARIANT_NUMERIC[variant]
    if variant not in TABS_VARIANTS:
        raise ValueError(f"Invalid tabs variant: {variant}")
    return variant


# Аналогичная функция для Accordion
def normalize_accordion_variant(variant: str | int) -> str:
    if isinstance(variant, int):
        if variant not in ACCORDION_VARIANT_NUMERIC:
            raise ValueError(f"Invalid accordion variant: {variant}")
        return ACCORDION_VARIANT_NUMERIC[variant]
    if variant not in ACCORDION_VARIANTS:
        raise ValueError(f"Invalid accordion variant: {variant}")
    return variant


# Конфигурация для переиспользуемых компонентов, таких как Tabs и Accordion, с нормализацией вариантов оформления
@dataclass(frozen=True)
class TabsComponentConfig:
    variant: str = "default"


# Конфигурация для Accordion компонента, с нормализацией вариантов оформления
@dataclass(frozen=True)
class AccordionComponentConfig:
    variant: str = "default"


# Общая конфигурация для всех переиспользуемых компонентов, с дефолтными настройками для Tabs и Accordion
@dataclass(frozen=True)
class ComponentConfig:
    tabs: TabsComponentConfig = field(default_factory=TabsComponentConfig)
    accordion: AccordionComponentConfig = field(
        default_factory=AccordionComponentConfig
    )


# Элемент конфигурации таба на странице
@dataclass(frozen=True)
class PageTabsItem:
    tab_id: str
    title: str
    href: str
    disabled: bool = False


# Конфигурация табов на странице, с дефолтным вариантом оформления и параметром для определения активного таба через query param
@dataclass(frozen=True)
class PageTabsConfig:
    variant: str = "default"
    active_param: str = "tab"
    items: tuple[PageTabsItem, ...] = field(default_factory=tuple)


# Конфигурация маршрута страницы, с возможностью указания режима отображения страницы
@dataclass(frozen=True)
class PageRouteConfig:
    mode: str | None = None


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
    tabs: PageTabsConfig | None = None
    route: PageRouteConfig = field(default_factory=PageRouteConfig)


# Полная read-only конфигурация BeeUI, собранная из schema.yml
@dataclass(frozen=True)
class BeeUiConfig:
    app_title: str
    product: str
    logo_text: str
    locale: LocaleConfig
    theme: ThemeConfig
    layout: LayoutConfig
    navigation: list[BeeUiNavigationItem]
    data_sources: dict[str, DataSourceDefinition]
    blocks: dict[str, BlockDefinition]
    pages: list[BeeUiPage]
    components: ComponentConfig = field(default_factory=ComponentConfig)
