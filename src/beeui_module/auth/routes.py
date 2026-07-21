from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from beeui_module.auth.dependencies import require_session
from beeui_module.auth.models import SessionData
from beeui_module.auth.service import AuthService
from beeui_module.pages.links import effective_external_prefix
from beeui_module.pages.locale import resolve_locale as _resolve_locale, translate


def register_auth_routes(
    *,
    app: Any,
    templates: Jinja2Templates,
    route_prefix: str,
) -> None:
    router = APIRouter(prefix=route_prefix or "")

    def _external_prefix(request: Request) -> str:
        return effective_external_prefix(request, route_prefix)

    def _root_href(request: Request) -> str:
        return f"{_external_prefix(request)}/" if _external_prefix(request) else "/"

    def _auth_locale(request: Request) -> str:
        state = getattr(request.app, "state", None)
        ui_config = getattr(state, "beeui_ui_config", None) if state else None
        if ui_config is not None:
            locale_cfg = getattr(ui_config, "locale", None)
            if locale_cfg is not None:
                return _resolve_locale(
                    request, locale_cfg.default, locale_cfg.available
                )
        lang = request.query_params.get("lang")
        if lang == "ru":
            return "ru"
        cookie_lang = request.cookies.get("beeui_lang")
        if cookie_lang == "ru":
            return "ru"
        return "en"

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
                    "route_prefix": _external_prefix(request),
                    "locale": _auth_locale(request),
                    "auth_disabled": True,
                    "error": None,
                },
            )

        session = _get_session_if_valid(request, service)
        if session is not None:
            return RedirectResponse(
                url=_root_href(request),
                status_code=302,
            )

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "route_prefix": _external_prefix(request),
                "locale": _auth_locale(request),
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
                    "route_prefix": _external_prefix(request),
                    "locale": _auth_locale(request),
                    "auth_disabled": True,
                    "error": translate("auth.disabled", _auth_locale(request)),
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
                        "route_prefix": _external_prefix(request),
                        "locale": _auth_locale(request),
                    "auth_disabled": False,
                        "error": translate("auth.invalid_form", _auth_locale(request)),
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
                        "route_prefix": _external_prefix(request),
                        "locale": _auth_locale(request),
                        "auth_disabled": False,
                        "error": translate("auth.required", _auth_locale(request)),
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
                        "route_prefix": _external_prefix(request),
                        "locale": _auth_locale(request),
                        "auth_disabled": False,
                        "error": "Неверные учётные данные" if _auth_locale(request) == 'ru' else "Invalid credentials",
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
            url=_root_href(request),
            status_code=302,
        )
        response.set_cookie(
            key=service.cookie_name(),
            value=cookie,
            httponly=True,
            secure=service.cookie_secure,
            samesite="lax",
            max_age=86400,
            path=_external_prefix(request) or "/",
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
                url=f"{_external_prefix(request)}/auth/login",
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
            path=_external_prefix(request) or "/",
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
