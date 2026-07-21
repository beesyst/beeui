from __future__ import annotations

from urllib.parse import unquote, urlencode, urlsplit, urlunsplit

ALLOWED_PRESERVED_PARAMS = frozenset({"lang", "period", "run_id"})


def effective_external_prefix(request: object, route_prefix: str) -> str:
    scope = getattr(request, "scope", {})
    if not isinstance(scope, dict):
        scope = {}
    root_path = str(scope.get("root_path") or "").rstrip("/")
    local_prefix = route_prefix.rstrip("/")
    return f"{root_path}{local_prefix}"


def preserve_allowed_params(
    params: dict[str, str] | None,
    allowlist: frozenset[str] | None = None,
) -> dict[str, str]:
    if params is None:
        return {}
    allowed = allowlist if allowlist is not None else ALLOWED_PRESERVED_PARAMS
    return {
        k: v
        for k, v in params.items()
        if k in allowed and isinstance(v, str) and v.strip()
    }


def add_preserved_params_to_href(
    href: str,
    current_params: dict[str, str],
    allowlist: frozenset[str] | None = None,
) -> str | None:
    preserved = preserve_allowed_params(current_params, allowlist)
    if not preserved:
        return href
    try:
        parsed = urlsplit(href)
    except (TypeError, ValueError):
        return None
    existing_qs = parsed.query
    existing_params: dict[str, str] = {}
    if existing_qs:
        for part in existing_qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                existing_params[k] = v
    merged = dict(existing_params)
    merged.update(preserved)
    qs = urlencode(sorted(merged.items()))
    return urlunsplit(("", "", parsed.path, qs, parsed.fragment))


def is_safe_internal_href(href: str) -> bool:
    try:
        parsed = urlsplit(href)
    except (TypeError, ValueError):
        return False
    if parsed.scheme or parsed.netloc or href.startswith("//"):
        return False
    if "\\" in href:
        return False
    decoded_path = unquote(parsed.path)
    segments = decoded_path.split("/")
    if any(segment in {".", ".."} for segment in segments):
        return False
    if "//" in decoded_path:
        return False
    return True


def validate_internal_href(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    href = value.strip()
    if not href or not href.startswith("/"):
        return None
    try:
        parsed = urlsplit(href)
    except (TypeError, ValueError):
        return None
    decoded_href = unquote(href)
    decoded_path = unquote(parsed.path)
    if (
        any(ord(char) < 32 for char in href)
        or any(ord(char) < 32 for char in decoded_href)
        or "\\" in decoded_href
        or "//" in decoded_path
        or any(part in {".", ".."} for part in decoded_path.split("/"))
        or not is_safe_internal_href(href)
    ):
        return None
    return href


def prefix_internal_href(route_prefix: str, href: str) -> str | None:
    try:
        parsed = urlsplit(href)
    except (TypeError, ValueError):
        return None
    prefix = route_prefix.rstrip("/")
    path = parsed.path
    if prefix and path != prefix and not path.startswith(f"{prefix}/"):
        path = f"{prefix}{path}"
    return urlunsplit(("", "", path, parsed.query, parsed.fragment))
