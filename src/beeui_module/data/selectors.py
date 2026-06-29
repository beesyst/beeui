from __future__ import annotations

import re
from typing import Any

_SELECTOR_RE = re.compile(
    r"^[A-Za-z][A-Za-z0-9_]*(\[\d+\])*(\.[A-Za-z][A-Za-z0-9_]*(\[\d+\])*)*$"
)
_SEGMENT_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]*|\[(\d+)\]")


def validate_selector(selector: str) -> list[str | int]:
    if not isinstance(selector, str) or not selector.strip():
        raise ValueError("selector must be a non-empty string")

    normalized = selector.strip()
    if not _SELECTOR_RE.fullmatch(normalized):
        raise ValueError(f"Invalid selector syntax: {normalized}")

    tokens: list[str | int] = []
    for segment in normalized.split("."):
        position = 0
        for match in _SEGMENT_RE.finditer(segment):
            if match.start() != position:
                raise ValueError(f"Invalid selector syntax: {normalized}")
            value = match.group(0)
            if value.startswith("["):
                tokens.append(int(match.group(1)))
            else:
                if value.startswith("__"):
                    raise ValueError(f"Invalid selector syntax: {normalized}")
                tokens.append(value)
            position = match.end()
        if position != len(segment):
            raise ValueError(f"Invalid selector syntax: {normalized}")

    return tokens


def select_data(payload: Any, selector: str) -> Any:
    current = payload
    for token in validate_selector(selector):
        if isinstance(token, str):
            if not isinstance(current, dict) or token not in current:
                raise KeyError(selector)
            current = current[token]
            continue

        if not isinstance(current, list) or token >= len(current):
            raise KeyError(selector)
        current = current[token]

    return current
