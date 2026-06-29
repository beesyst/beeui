from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from beeui_module.auth.models import SessionData

_SESSION_COOKIE_NAME = "beeui_session"
_SESSION_MAX_AGE = 86400
_HMAC_DIGEST = hashlib.sha256


def _sign(payload: str, secret: str) -> str:
    mac = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        _HMAC_DIGEST,
    )
    return base64.urlsafe_b64encode(mac.digest()).decode("ascii").rstrip("=")


def _encode_data(data: dict[str, Any]) -> str:
    raw = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=")


def _decode_data(encoded: str) -> dict[str, Any] | None:
    try:
        padded = encoded + "=" * (4 - len(encoded) % 4)
        raw = base64.urlsafe_b64decode(padded)
        return json.loads(raw)
    except Exception:
        return None


def create_session_cookie(session: SessionData, secret: str) -> str:
    data = session.to_dict()
    encoded = _encode_data(data)
    sig = _sign(encoded, secret)
    return f"{encoded}.{sig}"


def verify_session_cookie(cookie: str, secret: str) -> SessionData | None:
    if not cookie or "." not in cookie:
        return None

    encoded, sig = cookie.rsplit(".", 1)
    expected_sig = _sign(encoded, secret)

    if not hmac.compare_digest(sig, expected_sig):
        return None

    data = _decode_data(encoded)
    if data is None:
        return None

    created_at = float(data.get("created_at", 0))
    if time.time() - created_at > _SESSION_MAX_AGE:
        return None

    try:
        return SessionData.from_dict(data)
    except KeyError, ValueError, TypeError:
        return None


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def session_cookie_name() -> str:
    return _SESSION_COOKIE_NAME
