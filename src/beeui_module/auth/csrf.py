from __future__ import annotations

import hmac

from beeui_module.auth.sessions import generate_csrf_token


# Чек CSRF токена: сравнение предоставленного токена с ожидаемым, возвращая True при совпадении
def validate_csrf_token(
    provided_token: str,
    expected_token: str,
) -> bool:
    if not provided_token or not expected_token:
        return False
    return hmac.compare_digest(provided_token, expected_token)


__all__ = [
    "generate_csrf_token",
    "validate_csrf_token",
]
