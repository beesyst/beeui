from __future__ import annotations

from markupsafe import Markup

from beeui_module.pages.models import (
    TABS_ICON_NAMES,
    TABS_ICON_SVGS,
)

_ICON_ATTRS = (
    'class="icon me-2" '
    'data-beeui-tab-icon="{name}" '
    'width="20" height="20" '
    'viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" '
    'stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true"'
)


def tab_icon_svg(icon: str | None) -> Markup:
    if not icon or icon not in TABS_ICON_SVGS:
        return Markup("")
    body = "".join(f'<path d="{path}"/>' for path in TABS_ICON_SVGS[icon])
    return Markup(f"<svg {_ICON_ATTRS.format(name=icon)}>{body}</svg>")


def supported_tab_icon_names() -> tuple[str, ...]:
    return tuple(TABS_ICON_NAMES)
