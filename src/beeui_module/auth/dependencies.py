from __future__ import annotations

from fastapi import HTTPException, Request

from beeui_module.auth.csrf import validate_csrf_token
from beeui_module.auth.models import SessionData, UserRole
from beeui_module.auth.service import AuthService

_CSRF_HEADER = "X-CSRF-Token"
_CSRF_FORM_FIELD = "csrf_token"


# Зависимости для маршрутов аутентификации
def _get_auth_service(request: Request) -> AuthService:
    service: AuthService | None = getattr(request.app.state, "beeui_auth_service", None)
    if service is None:
        raise HTTPException(status_code=500, detail="Auth service not configured")
    return service


# Извлечение и проверка сессии из cookie
def require_session(request: Request) -> SessionData:
    service = _get_auth_service(request)

    if not service.enabled:
        return SessionData(
            user_id="local",
            role=UserRole.viewer,
            csrf_token="",
        )

    cookie_name = service.cookie_name()
    cookie = request.cookies.get(cookie_name)
    session = service.verify_session(cookie)

    if session is None:
        raise HTTPException(
            status_code=401,
            detail={
                "ok": False,
                "api": "beeui.v0",
                "read_only": True,
                "error": {
                    "code": "unauthenticated",
                    "message": "Authentication required",
                },
                "warnings": [],
                "meta": {},
            },
        )

    return session


# Фабрика зависимости: требование сессии с определенной минимальной ролью
def require_role(minimum_role: UserRole):
    async def _check_role(request: Request) -> SessionData:
        session = require_session(request)
        service = _get_auth_service(request)

        if service.enabled and not service.check_role(session, minimum_role):
            raise HTTPException(
                status_code=403,
                detail={
                    "ok": False,
                    "api": "beeui.v0",
                    "read_only": True,
                    "error": {
                        "code": "forbidden",
                        "message": f"Insufficient role: {session.role.value}",
                    },
                    "warnings": [],
                    "meta": {},
                },
            )

        return session

    return _check_role


# Валидация секции security
async def require_csrf(request: Request) -> None:
    service = _get_auth_service(request)

    if not service.enabled:
        return

    session = require_session(request)

    csrf_token = request.headers.get(_CSRF_HEADER) or ""

    if not csrf_token:
        try:
            form = await request.form()
            form_value = form.get(_CSRF_FORM_FIELD, "")
            csrf_token = form_value if isinstance(form_value, str) else ""
        except Exception:
            pass

    if not validate_csrf_token(csrf_token, session.csrf_token):
        raise HTTPException(
            status_code=403,
            detail={
                "ok": False,
                "api": "beeui.v0",
                "read_only": True,
                "error": {
                    "code": "csrf_failed",
                    "message": "CSRF validation failed",
                },
                "warnings": [],
                "meta": {},
            },
        )
