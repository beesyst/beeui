from __future__ import annotations

from dataclasses import dataclass, field

from beeui_module.blocks.models import BlockDefinition, BlockPlacement
from beeui_module.data.models import DataSourceDefinition

LocalizedText = str | dict[str, str]


@dataclass(frozen=True)
class LocaleConfig:
    default: str = "en"
    available: tuple[str, ...] = ("en",)


@dataclass(frozen=True)
class ThemeConfig:
    mode: str
    primary: str
    base: str
    font: str
    radius: int
    density: str


@dataclass(frozen=True)
class SidebarConfig:
    variant: str
    collapsed: bool


@dataclass(frozen=True)
class NavbarConfig:
    enabled: bool
    variant: str
    sticky: bool


@dataclass(frozen=True)
class LayoutConfig:
    type: str
    container: str
    sidebar: SidebarConfig
    navbar: NavbarConfig


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


def normalize_tabs_variant(variant: str | int) -> str:
    if isinstance(variant, int):
        if variant not in TABS_VARIANT_NUMERIC:
            raise ValueError(f"Invalid tabs variant: {variant}")
        return TABS_VARIANT_NUMERIC[variant]
    if variant not in TABS_VARIANTS:
        raise ValueError(f"Invalid tabs variant: {variant}")
    return variant


def normalize_accordion_variant(variant: str | int) -> str:
    if isinstance(variant, int):
        if variant not in ACCORDION_VARIANT_NUMERIC:
            raise ValueError(f"Invalid accordion variant: {variant}")
        return ACCORDION_VARIANT_NUMERIC[variant]
    if variant not in ACCORDION_VARIANTS:
        raise ValueError(f"Invalid accordion variant: {variant}")
    return variant


@dataclass(frozen=True)
class TabsComponentConfig:
    variant: str = "default"


@dataclass(frozen=True)
class AccordionComponentConfig:
    variant: str = "default"


@dataclass(frozen=True)
class ComponentConfig:
    tabs: TabsComponentConfig = field(default_factory=TabsComponentConfig)
    accordion: AccordionComponentConfig = field(
        default_factory=AccordionComponentConfig
    )


@dataclass(frozen=True)
class PageTabsItem:
    tab_id: str
    title: LocalizedText
    href: str
    disabled: bool = False


@dataclass(frozen=True)
class PageTabsConfig:
    variant: str = "default"
    active_param: str = "tab"
    items: tuple[PageTabsItem, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PageRouteConfig:
    mode: str | None = None


@dataclass(frozen=True)
class BeeUiNavigationItem:
    title: LocalizedText
    path: str | None = None
    icon: str | None = None
    disabled: bool = False
    children: list["BeeUiNavigationItem"] = field(default_factory=list)


@dataclass(frozen=True)
class BeeUiPage:
    page_id: str
    path: str
    title: LocalizedText
    subtitle: LocalizedText | None
    blocks: list[BlockPlacement]
    tabs: PageTabsConfig | None = None
    route: PageRouteConfig = field(default_factory=PageRouteConfig)


@dataclass(frozen=True)
class BeeUiConfig:
    app_title: LocalizedText
    product: str
    logo_text: LocalizedText
    locale: LocaleConfig
    theme: ThemeConfig
    layout: LayoutConfig
    navigation: list[BeeUiNavigationItem]
    data_sources: dict[str, DataSourceDefinition]
    blocks: dict[str, BlockDefinition]
    pages: list[BeeUiPage]
    components: ComponentConfig = field(default_factory=ComponentConfig)
