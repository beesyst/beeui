from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from beeui_module.auth.dependencies import require_session
from beeui_module.auth.models import SessionData
from beeui_module.auth.service import AuthService


def register_auth_routes(
    *,
    app: Any,
    templates: Jinja2Templates,
    route_prefix: str,
) -> None:
    router = APIRouter(prefix=route_prefix or "")

    login_path = "/auth/login"
    logout_path = "/auth/logout"
    csrf_path = "/auth/csrf"

    @router.get(
        login_path,
        response_class=HTMLResponse,
        response_model=None,
        include_in_schema=False,
    )
    async def login_form(request: Request):
        service = _get_service(request)
        if not service.enabled:
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "request": request,
                    "route_prefix": route_prefix or "",
                    "auth_disabled": True,
                    "error": None,
                },
            )

        session = _get_session_if_valid(request, service)
        if session is not None:
            return RedirectResponse(
                url=f"{route_prefix or ''}/",
                status_code=302,
            )

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "route_prefix": route_prefix or "",
                "auth_disabled": False,
                "error": None,
            },
        )

    @router.post(login_path, response_model=None, include_in_schema=False)
    async def login_action(request: Request):
        service = _get_service(request)

        if not service.enabled:
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "request": request,
                    "route_prefix": route_prefix or "",
                    "auth_disabled": True,
                    "error": "Auth is disabled in local/dev mode",
                },
                status_code=400,
            )

        accept = request.headers.get("accept", "")
        wants_html = "text/html" in accept

        try:
            form = await request.form()
            raw_user_id = form.get("user_id", "")
            raw_token = form.get("token", "")
            user_id = raw_user_id.strip() if isinstance(raw_user_id, str) else ""
            token = raw_token.strip() if isinstance(raw_token, str) else ""
        except Exception:
            if wants_html:
                return templates.TemplateResponse(
                    request=request,
                    name="login.html",
                    context={
                        "request": request,
                        "route_prefix": route_prefix or "",
                        "auth_disabled": False,
                        "error": "Invalid form data",
                    },
                    status_code=400,
                )
            return JSONResponse(
                {
                    "ok": False,
                    "api": "beeui.v0",
                    "read_only": True,
                    "error": {
                        "code": "invalid_input",
                        "message": "Invalid form data",
                    },
                    "warnings": [],
                    "meta": {},
                },
                status_code=400,
            )

        if not user_id or not token:
            if wants_html:
                return templates.TemplateResponse(
                    request=request,
                    name="login.html",
                    context={
                        "request": request,
                        "route_prefix": route_prefix or "",
                        "auth_disabled": False,
                        "error": "User ID and token are required",
                    },
                    status_code=400,
                )
            return JSONResponse(
                {
                    "ok": False,
                    "api": "beeui.v0",
                    "read_only": False,
                    "error": {
                        "code": "invalid_input",
                        "message": "User ID and token are required",
                    },
                    "warnings": [],
                    "meta": {},
                },
                status_code=400,
            )

        session, cookie = service.authenticate(user_id, token)

        if session is None or cookie is None:
            if wants_html:
                return templates.TemplateResponse(
                    request=request,
                    name="login.html",
                    context={
                        "request": request,
                        "route_prefix": route_prefix or "",
                        "auth_disabled": False,
                        "error": "Invalid credentials",
                    },
                    status_code=401,
                )
            return JSONResponse(
                {
                    "ok": False,
                    "api": "beeui.v0",
                    "read_only": True,
                    "error": {
                        "code": "authentication_failed",
                        "message": "Invalid credentials",
                    },
                    "warnings": [],
                    "meta": {},
                },
                status_code=401,
            )

        response = RedirectResponse(
            url=f"{route_prefix or ''}/",
            status_code=302,
        )
        response.set_cookie(
            key=service.cookie_name(),
            value=cookie,
            httponly=True,
            secure=service.cookie_secure,
            samesite="lax",
            max_age=86400,
            path=route_prefix or "/",
        )
        return response

    @router.post(logout_path, response_model=None, include_in_schema=False)
    async def logout_action(
        request: Request,
        session: SessionData = Depends(require_session),
    ):
        service = _get_service(request)
        accept = request.headers.get("accept", "")
        wants_html = "text/html" in accept

        if wants_html:
            response = RedirectResponse(
                url=f"{route_prefix or ''}/auth/login",
                status_code=302,
            )
        else:
            response = JSONResponse(
                {
                    "ok": True,
                    "api": "beeui.v0",
                    "read_only": True,
                    "data": {"message": "Logged out"},
                    "warnings": [],
                    "meta": {},
                }
            )

        response.delete_cookie(
            key=service.cookie_name(),
            path=route_prefix or "/",
        )
        return response

    @router.get(csrf_path, response_model=None, include_in_schema=False)
    async def get_csrf_token(
        request: Request,
        session: SessionData = Depends(require_session),
    ):
        return JSONResponse(
            {
                "ok": True,
                "api": "beeui.v0",
                "read_only": True,
                "data": {"csrf_token": session.csrf_token},
                "warnings": [],
                "meta": {},
            }
        )

    app.include_router(router)


def _get_service(request: Request) -> AuthService:
    service: AuthService | None = getattr(request.app.state, "beeui_auth_service", None)
    if service is None:
        raise HTTPException(status_code=500, detail="Auth service not configured")
    return service


def _get_session_if_valid(request: Request, service: AuthService) -> SessionData | None:
    cookie_name = service.cookie_name()
    cookie = request.cookies.get(cookie_name)
    return service.verify_session(cookie)
