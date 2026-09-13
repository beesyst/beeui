from __future__ import annotations

import re

_ICON_NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def is_safe_icon_name(value: object) -> bool:
    return isinstance(value, str) and bool(_ICON_NAME_RE.fullmatch(value))


def safe_icon_name(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return value if is_safe_icon_name(value) else None
