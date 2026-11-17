from __future__ import annotations

import json
import re

from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser

from beeui_module.adapters.envelopes import AdapterErrorResult, AdapterResult
from beeui_module.api.envelopes import async_safe_adapter_call
from beeui_module.artifacts.redaction import redact_value
from beeui_module.auth.dependencies import require_csrf, require_role, require_session
from beeui_module.auth.models import UserRole


def register_upload_routes(app, route_prefix, adapter):
    actions = getattr(adapter, "upload_actions", {})
    if not actions:
        return
    if not isinstance(actions, dict) or any(
        not isinstance(key, str)
        or re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", key) is None
        or not callable(callback)
        for key, callback in actions.items()
    ):
        raise ValueError("Invalid registered upload actions")
    actions = dict(actions)

    async def upload_csrf(request: Request):
        if not request.app.state.beeui_auth_service.enabled or not request.headers.get(
            "X-CSRF-Token"
        ):
            raise HTTPException(403, "Protected upload requires session and CSRF")
        await require_csrf(request)

    @app.post(f"{route_prefix}/api/actions/upload", include_in_schema=False)
    async def upload(
        request: Request,
        _role=Depends(require_role(UserRole.operator)),
        _csrf=Depends(upload_csrf),
    ):
        async def bounded_stream():
            size = 0
            async for chunk in request.stream():
                size += len(chunk)
                if size > 17 * 1024 * 1024:
                    raise MultiPartException("Upload limit")
                yield chunk

        form = None
        try:
            parser = MultiPartParser(
                request.headers,
                bounded_stream(),
                max_files=8,
                max_fields=2,
                max_part_size=65536,
            )
            form = await parser.parse()
            action_id = form.get("action_id")
            raw = form.get("payload")
            if not isinstance(action_id, str) or action_id not in actions:
                raise ValueError("Unregistered upload")
            if not isinstance(raw, str) or len(raw) > 49152:
                raise ValueError("Invalid upload arguments")
            payload = json.loads(raw)
            if not isinstance(payload, dict) or len(payload) > 10:
                raise ValueError("Invalid upload arguments")
            if any(
                not isinstance(k, str) or not isinstance(v, str) or len(v) > 4096
                for k, v in payload.items()
            ):
                raise ValueError("Invalid upload arguments")
            entries = form.multi_items()
            if (
                sum(key == "action_id" for key, _ in entries) != 1
                or sum(key == "payload" for key, _ in entries) != 1
            ):
                raise ValueError("Duplicate upload arguments")
            files = []
            for key, item in entries:
                if key in {"action_id", "payload"}:
                    continue
                if key != "files" or not isinstance(item, UploadFile):
                    raise ValueError("Invalid upload field")
                content = await item.read(2097153)
                if not content or len(content) > 2097152:
                    raise ValueError("Invalid upload size")
                files.append(
                    {
                        "filename": item.filename,
                        "content_type": item.content_type,
                        "content": content,
                    }
                )
            if not 1 <= len(files) <= 8:
                raise ValueError("Invalid upload count")
            session = require_session(request)
            result = await async_safe_adapter_call(
                actions[action_id],
                payload,
                files,
                {"user_id": session.user_id, "role": session.role.value},
            )
            if isinstance(result, AdapterErrorResult) or not isinstance(
                result, AdapterResult
            ):
                raise ValueError("Upload refused")
            return JSONResponse(
                {
                    "ok": True,
                    "api": "beeui.v0",
                    "read_only": False,
                    "data": redact_value(result.data),
                    "warnings": [],
                    "meta": {},
                },
                headers={"Cache-Control": "no-store"},
            )
        except ValueError, TypeError, KeyError, MultiPartException, UnicodeError:
            raise HTTPException(400, "Upload refused") from None
        finally:
            if form is not None:
                await form.close()
