from __future__ import annotations

import hmac
import logging
from typing import Any

from beeui_module.auth.models import SessionData, UserRole, role_meets_minimum
from beeui_module.auth.sessions import (
    create_session_cookie,
    generate_csrf_token,
    session_cookie_name,
    verify_session_cookie,
)

logger = logging.getLogger("beeui.auth")


# Класс: сервис аутентификации, который управляет настройками, проверкой токенов и сессий, а также ролями пользователей
class AuthService:
    def __init__(self, settings_auth: dict[str, Any]) -> None:
        self._enabled = bool(settings_auth.get("enabled", False))
        self._session_secret: str | None = settings_auth.get("session_secret")
        self._operator_token: str | None = settings_auth.get("operator_token")
        self._admin_token: str | None = settings_auth.get("admin_token")
        self._cookie_secure = bool(settings_auth.get("cookie_secure", False))

    @property
    def enabled(self) -> bool:
        return self._enabled

    def validate_startup(self) -> None:
        if not self._enabled:
            logger.info("Auth is disabled (local/dev mode)")
            return

        errors: list[str] = []

        if not self._session_secret:
            errors.append(
                "auth.session_secret is required when auth is enabled; "
                "set BEEUI_SESSION_SECRET env var"
            )
        if not self._operator_token:
            errors.append(
                "auth.operator_token is required when auth is enabled; "
                "set BEEUI_OPERATOR_TOKEN env var"
            )
        if not self._admin_token:
            errors.append(
                "auth.admin_token is required when auth is enabled; "
                "set BEEUI_ADMIN_TOKEN env var"
            )

        if errors:
            msg = "; ".join(errors)
            logger.error("Auth startup validation failed: %s", msg)
            raise ValueError(msg)

        logger.info("Auth is enabled (session/role/CSRF mode)")

    def authenticate(
        self, user_id: str, token: str
    ) -> tuple[SessionData | None, str | None]:
        if not self._enabled:
            return None, None

        role = self._resolve_role(token)
        if role is None:
            logger.warning("Authentication failed for user_id=%s", user_id)
            return None, None

        csrf_token = generate_csrf_token()
        session = SessionData(
            user_id=user_id,
            role=role,
            csrf_token=csrf_token,
        )
        cookie = create_session_cookie(session, self._session_secret or "")
        logger.info("Session created for user_id=%s role=%s", user_id, role.value)
        return session, cookie

    def verify_session(self, cookie: str | None) -> SessionData | None:
        if not self._enabled or not cookie:
            return None
        secret = self._session_secret or ""
        return verify_session_cookie(cookie, secret)

    def check_role(self, session: SessionData, minimum_role: UserRole) -> bool:
        """Check if session has at least the minimum role."""
        return role_meets_minimum(session.role, minimum_role)

    def _resolve_role(self, token: str) -> UserRole | None:
        if not token:
            return None
        if self._admin_token and hmac.compare_digest(token, self._admin_token):
            return UserRole.admin
        if self._operator_token and hmac.compare_digest(token, self._operator_token):
            return UserRole.operator
        return None

    @property
    def cookie_secure(self) -> bool:
        return self._cookie_secure

    def cookie_name(self) -> str:
        return session_cookie_name()
