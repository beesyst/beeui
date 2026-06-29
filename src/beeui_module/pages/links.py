from __future__ import annotations

from urllib.parse import unquote, urlencode, urlsplit, urlunsplit

ALLOWED_PRESERVED_PARAMS = frozenset({"lang", "period", "run_id"})


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
) -> str:
    preserved = preserve_allowed_params(current_params, allowlist)
    if not preserved:
        return href
    parsed = urlsplit(href)
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
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith("//"):
        return False
    if "\\" in href:
        return False
    decoded_path = unquote(parsed.path)
    segments = decoded_path.split("/")
    if any(segment in {".", ".."} for segment in segments):
        return False
    if "//" in parsed.path:
        return False
    return True
