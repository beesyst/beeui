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
    {
        "default",
        "reverse",
        "fill",
        "icons",
        "fill_icons",
        "compact_fill_icons",
        "dropdown",
    }
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


TABS_ICON_NAMES = (
    "dashboard",
    "runs",
    "list",
    "reports",
    "chart",
    "calendar",
    "queue",
    "messages",
    "ai",
    "source",
    "attachment",
    "evidence",
    "integration",
    "recommendation",
    "ban",
)


TABS_ICON_SVGS: dict[str, tuple[str, ...]] = {
    "dashboard": (
        "M12 13m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0",
        "M13.45 11.55l2.05 -2.05",
        "M6.4 20a9 9 0 1 1 11.2 0z",
    ),
    "runs": ("M3 12h4l3 8l4 -16l3 8h4",),
    "list": (
        "M9 6l11 0",
        "M9 12l11 0",
        "M9 18l11 0",
        "M5 6l0 .01",
        "M5 12l0 .01",
        "M5 18l0 .01",
    ),
    "reports": (
        "M3 12m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v6a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z",
        "M9 8m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z",
        "M15 4m0 1a1 1 0 0 1 1 -1h4a1 1 0 0 1 1 1v14a1 1 0 0 1 -1 1h-4a1 1 0 0 1 -1 -1z",
        "M4 20l14 0",
    ),
    "chart": (
        "M4 19l16 0",
        "M4 15l4 -6l4 2l4 -5l4 4",
    ),
    "calendar": (
        "M4 7a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12z",
        "M16 3v4",
        "M8 3v4",
        "M4 11h16",
        "M11 15h1",
        "M12 15v3",
    ),
    "queue": (
        "M12 6l-8 4l8 4l8 -4l-8 -4",
        "M4 14l8 4l8 -4",
    ),
    "messages": (
        "M21 14l-3 -3h-7a1 1 0 0 1 -1 -1v-6a1 1 0 0 1 1 -1h9a1 1 0 0 1 1 1v10",
        "M14 15v2a1 1 0 0 1 -1 1h-7l-3 3v-10a1 1 0 0 1 1 -1h2",
    ),
    "ai": (
        "M6 4m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v4a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z",
        "M12 2v2",
        "M9 12v9",
        "M15 12v9",
        "M5 16l4 -2",
        "M15 14l4 2",
        "M9 18h6",
        "M10 8v.01",
        "M14 8v.01",
    ),
    "source": (
        "M12 6m-8 0a8 3 0 1 0 16 0a8 3 0 1 0 -16 0",
        "M4 6v6a8 3 0 0 0 16 0v-6",
        "M4 12v6a8 3 0 0 0 16 0v-6",
    ),
    "attachment": (
        "M15 7l-6.5 6.5a1.5 1.5 0 0 0 3 3l6.5 -6.5a3 3 0 0 0 -6 -6l-6.5 6.5a4.5 4.5 0 0 0 9 9l6.5 -6.5",
    ),
    "evidence": (
        "M10 10m-7 0a7 7 0 1 0 14 0a7 7 0 1 0 -14 0",
        "M21 21l-6 -6",
    ),
    "integration": (
        "M9 15l6 -6",
        "M11 6l.463 -.536a5 5 0 0 1 7.071 7.072l-.534 .464",
        "M13 18l-.397 .534a5.068 5.068 0 0 1 -7.127 0a4.972 4.972 0 0 1 0 -7.071l.524 -.463",
    ),
    "recommendation": (
        "M3 12h1m8 -9v1m8 8h1m-15.4 -6.4l.7 .7m12.1 -.7l-.7 .7",
        "M9 16a5 5 0 1 1 6 0a3.5 3.5 0 0 0 -1 3a2 2 0 0 1 -4 0a3.5 3.5 0 0 0 -1 -3",
        "M9.7 17l4.6 0",
    ),
    "ban": (
        "M10 10m-7 0a7 7 0 1 0 14 0a7 7 0 1 0 -14 0",
        "M5 5l14 14",
    ),
}


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
    icon: str | None = None


@dataclass(frozen=True)
class PageTabsConfig:
    variant: str = "default"
    active_param: str = "tab"
    items: tuple[PageTabsItem, ...] = field(default_factory=tuple)
    progressive: bool = False


@dataclass(frozen=True)
class PageRouteConfig:
    mode: str | None = None


@dataclass(frozen=True)
class BeeUiNavigationItem:
    title: LocalizedText
    path: str | None = None
    icon: str | None = None
    disabled: bool = False
    children: list[BeeUiNavigationItem] = field(default_factory=list)


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
