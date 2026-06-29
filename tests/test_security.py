from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from beeui_module.adapters.base import ProductUiAdapterBase
from beeui_module.adapters.envelopes import (
    AdapterErrorResult,
    AdapterMetadata,
    AdapterResult,
    ok_result,
)
from beeui_module.auth.models import SessionData, UserRole
from beeui_module.auth.service import AuthService
from beeui_module.auth.sessions import (
    create_session_cookie,
    session_cookie_name,
    verify_session_cookie,
)
from beeui_module.core.paths import settings_path
from beeui_module.core.settings import load_settings
from beeui_module.web.app import create_beeui_app

_TEST_SECRET = "test-session-secret-for-testing-only"
_TEST_OPERATOR_TOKEN = "test-operator-token"
_TEST_ADMIN_TOKEN = "test-admin-token"


def _set_viewer_session(client: TestClient) -> None:
    session = SessionData(
        user_id="viewer_user",
        role=UserRole.viewer,
        csrf_token="test-csrf-token",
    )
    cookie = create_session_cookie(session, _TEST_SECRET)
    client.cookies.set(session_cookie_name(), cookie)


def _make_auth_settings(
    *,
    enabled: bool = True,
    session_secret: str = _TEST_SECRET,
    operator_token: str = _TEST_OPERATOR_TOKEN,
    admin_token: str = _TEST_ADMIN_TOKEN,
    cookie_secure: bool = False,
) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "session_secret": session_secret,
        "operator_token": operator_token,
        "admin_token": admin_token,
        "cookie_secure": cookie_secure,
    }


def _create_app_with_auth(
    auth_cfg: dict[str, Any] | None = None,
) -> FastAPI:
    settings = load_settings(settings_path())
    if auth_cfg is not None:
        settings["auth"] = auth_cfg
    return create_beeui_app(settings=settings)


def _login(
    client: TestClient,
    user_id: str = "test_user",
    token: str = _TEST_ADMIN_TOKEN,
    route_prefix: str = "",
) -> TestClient:
    response = client.post(
        f"{route_prefix}/auth/login",
        data={"user_id": user_id, "token": token},
        follow_redirects=False,
    )
    assert response.status_code == 302, f"Login failed: {response.text}"
    cookie = response.cookies.get(session_cookie_name())
    assert cookie is not None, "No session cookie set"
    client.cookies.set(session_cookie_name(), cookie)
    return client


def test_auth_service_disabled_by_default() -> None:
    service = AuthService({"enabled": False})
    assert not service.enabled
    service.validate_startup()


def test_auth_service_enabled_fails_without_secret() -> None:
    service = AuthService({"enabled": True})
    with pytest.raises(ValueError, match="session_secret"):
        service.validate_startup()


def test_auth_service_enabled_fails_without_tokens() -> None:
    service = AuthService({"enabled": True, "session_secret": _TEST_SECRET})
    with pytest.raises(ValueError, match="operator_token"):
        service.validate_startup()


def test_auth_service_enabled_succeeds_with_all_config() -> None:
    service = AuthService(_make_auth_settings(enabled=True))
    service.validate_startup()


def test_auth_service_authenticate_valid_admin() -> None:
    service = AuthService(_make_auth_settings(enabled=True))
    session, cookie = service.authenticate("admin_user", _TEST_ADMIN_TOKEN)
    assert session is not None
    assert cookie is not None
    assert session.role == UserRole.admin
    assert session.user_id == "admin_user"


def test_auth_service_authenticate_valid_operator() -> None:
    service = AuthService(_make_auth_settings(enabled=True))
    session, cookie = service.authenticate("op_user", _TEST_OPERATOR_TOKEN)
    assert session is not None
    assert session.role == UserRole.operator


def test_auth_service_authenticate_invalid_token() -> None:
    service = AuthService(_make_auth_settings(enabled=True))
    session, cookie = service.authenticate("bad_user", "wrong-token")
    assert session is None
    assert cookie is None


def test_auth_service_authenticate_disabled() -> None:
    service = AuthService({"enabled": False})
    session, cookie = service.authenticate("user", "any-token")
    assert session is None
    assert cookie is None


def test_auth_service_role_check() -> None:
    service = AuthService(_make_auth_settings(enabled=True))

    viewer = SessionData(user_id="v", role=UserRole.viewer, csrf_token="t")
    operator = SessionData(user_id="o", role=UserRole.operator, csrf_token="t")
    admin = SessionData(user_id="a", role=UserRole.admin, csrf_token="t")

    assert not service.check_role(viewer, UserRole.operator)
    assert not service.check_role(viewer, UserRole.admin)
    assert service.check_role(operator, UserRole.viewer)
    assert service.check_role(operator, UserRole.operator)
    assert not service.check_role(operator, UserRole.admin)
    assert service.check_role(admin, UserRole.viewer)
    assert service.check_role(admin, UserRole.operator)
    assert service.check_role(admin, UserRole.admin)


def test_session_cookie_roundtrip() -> None:
    session = SessionData(
        user_id="test",
        role=UserRole.admin,
        csrf_token="csrf123",
    )
    cookie = create_session_cookie(session, _TEST_SECRET)
    assert cookie is not None
    assert "." in cookie

    verified = verify_session_cookie(cookie, _TEST_SECRET)
    assert verified is not None
    assert verified.user_id == "test"
    assert verified.role == UserRole.admin
    assert verified.csrf_token == "csrf123"


def test_session_cookie_invalid_signature() -> None:
    session = SessionData(
        user_id="test",
        role=UserRole.viewer,
        csrf_token="t",
    )
    cookie = create_session_cookie(session, _TEST_SECRET)
    tampered = cookie + "x"
    assert verify_session_cookie(tampered, _TEST_SECRET) is None


def test_session_cookie_wrong_secret() -> None:
    session = SessionData(
        user_id="test",
        role=UserRole.viewer,
        csrf_token="t",
    )
    cookie = create_session_cookie(session, _TEST_SECRET)
    assert verify_session_cookie(cookie, "wrong-secret") is None


def test_session_cookie_empty() -> None:
    assert verify_session_cookie("", _TEST_SECRET) is None
    assert verify_session_cookie(None, _TEST_SECRET) is None  # type: ignore


def test_session_cookie_malformed() -> None:
    assert verify_session_cookie("not-a-cookie", _TEST_SECRET) is None


def test_auth_disabled_app_starts() -> None:
    app = _create_app_with_auth({"enabled": False})
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_auth_disabled_login_returns_warning() -> None:
    app = _create_app_with_auth({"enabled": False})
    client = TestClient(app)
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "auth is disabled" in response.text.lower()


def test_login_success_creates_session() -> None:
    app = _create_app_with_auth(_make_auth_settings(enabled=True))
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        data={"user_id": "admin", "token": _TEST_ADMIN_TOKEN},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert session_cookie_name() in response.cookies


def test_login_failure_no_session() -> None:
    app = _create_app_with_auth(_make_auth_settings(enabled=True))
    client = TestClient(app)

    response = client.post(
        "/auth/login",
        data={"user_id": "admin", "token": "wrong-token"},
    )
    assert response.status_code == 401
    assert session_cookie_name() not in response.cookies


def test_logout_clears_session() -> None:
    app = _create_app_with_auth(_make_auth_settings(enabled=True))
    client = TestClient(app)

    _login(client)
    response = client.post(
        "/auth/logout",
        headers={"accept": "text/html"},
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_unauthenticated_post_returns_401() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True
    settings["features"]["config_apply"] = True
    settings["features"]["operator_actions"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)

    for path in (
        "/api/config/preview",
        "/api/config/apply",
        "/api/actions/preview",
        "/api/actions/execute",
    ):
        response = client.post(path, json={})
        assert response.status_code == 401, f"{path} should return 401"
        payload = response.json()
        assert "detail" not in payload, "Response must be top-level envelope"
        assert payload["error"]["code"] == "unauthenticated"


def test_missing_csrf_returns_403() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _login(client)

    response = client.post("/api/config/preview", json={})
    assert response.status_code == 403, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert "detail" not in payload, "Response must be top-level envelope"
    assert payload["error"]["code"] == "csrf_failed"


def test_valid_csrf_accepted() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _login(client)

    csrf_resp = client.get("/auth/csrf")
    assert csrf_resp.status_code == 200
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/preview",
        json={},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code not in (401, 403), (
        f"Got {response.status_code}: {response.text}"
    )


def test_viewer_cannot_call_config_apply() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_apply"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _set_viewer_session(client)

    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/apply",
        json={},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 403
    payload = response.json()
    assert "detail" not in payload, "Response must be top-level envelope"
    assert payload["error"]["code"] == "forbidden"


def test_operator_can_call_action_preview() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)

    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/actions/preview",
        json={"action_id": "test", "payload": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code not in (401, 403)


def test_no_adapter_call_when_unauthenticated() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    call_count = 0

    class TrackingAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def validate_config_candidate(
            self, candidate: dict
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def apply_config_candidate(
            self,
            candidate: dict,
            expected_hash: str | None = None,
            actor: dict | None = None,
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def list_actions(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def preview_action(
            self, action_id: str, payload: dict
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def execute_action(
            self,
            action_id: str,
            payload: dict,
            actor: dict | None = None,
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

    app = create_beeui_app(
        settings=settings,
        adapter=TrackingAdapter(),
    )
    client = TestClient(app)

    client.post("/api/config/preview", json={})
    assert call_count == 0, "Adapter called without authentication"


def test_config_routes_not_registered_when_disabled() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = False
    settings["features"]["config_apply"] = False
    settings["features"]["operator_actions"] = False

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _login(client)

    for path in (
        "/api/config/preview",
        "/api/config/apply",
        "/api/actions/preview",
        "/api/actions/execute",
    ):
        csrf_resp = client.get("/auth/csrf")
        csrf_token = csrf_resp.json()["data"]["csrf_token"]
        response = client.post(path, json={}, headers={"X-CSRF-Token": csrf_token})
        assert response.status_code == 404, f"{path} should be 404 when disabled"


def test_settings_validation_rejects_auth_without_secret() -> None:
    from beeui_module.core.settings import _validate_auth

    with pytest.raises(ValueError, match="session_secret"):
        _validate_auth(
            {
                "auth": {
                    "enabled": True,
                    "cookie_secure": False,
                    "operator_token": "op",
                    "admin_token": "admin",
                }
            }
        )


def test_settings_validation_accepts_disabled_auth() -> None:
    from beeui_module.core.settings import _validate_auth

    _validate_auth(
        {
            "auth": {
                "enabled": False,
                "session_secret": None,
                "operator_token": None,
                "admin_token": None,
            }
        }
    )


def test_auth_env_ref_resolved_successfully() -> None:
    import os

    os.environ["TEST_BEEUI_SESSION_SECRET"] = "env-secret"
    os.environ["TEST_BEEUI_OPERATOR_TOKEN"] = "env-op-token"
    os.environ["TEST_BEEUI_ADMIN_TOKEN"] = "env-admin-token"
    try:
        settings = load_settings(settings_path())
        settings["auth"] = {
            "enabled": True,
            "session_secret": "${TEST_BEEUI_SESSION_SECRET}",
            "operator_token": "${TEST_BEEUI_OPERATOR_TOKEN}",
            "admin_token": "${TEST_BEEUI_ADMIN_TOKEN}",
            "cookie_secure": False,
        }
        app = create_beeui_app(settings=settings)
        assert app.state.beeui_auth_service is not None
        assert app.state.beeui_auth_service.enabled
    finally:
        del os.environ["TEST_BEEUI_SESSION_SECRET"]
        del os.environ["TEST_BEEUI_OPERATOR_TOKEN"]
        del os.environ["TEST_BEEUI_ADMIN_TOKEN"]


def test_auth_env_ref_missing_fails_fast() -> None:
    from beeui_module.core.settings import load_settings

    settings = load_settings(settings_path())
    settings["auth"] = {
        "enabled": True,
        "session_secret": "${MISSING_ENV_SECRET}",
        "operator_token": "op-token",
        "admin_token": "admin-token",
        "cookie_secure": False,
    }
    with pytest.raises(
        ValueError,
        match="auth.session_secret must resolve to a non-empty string",
    ):
        create_beeui_app(settings=settings)


def test_unauthenticated_returns_top_level_envelope() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)

    response = client.post("/api/config/preview", json={})
    assert response.status_code == 401
    payload = response.json()
    assert "detail" not in payload
    assert payload["error"]["code"] == "unauthenticated"


def test_forbidden_returns_top_level_envelope() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_apply"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _set_viewer_session(client)

    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/apply",
        json={},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 403
    payload = response.json()
    assert "detail" not in payload
    assert payload["error"]["code"] == "forbidden"


def test_csrf_failed_returns_top_level_envelope() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _login(client)

    response = client.post("/api/config/preview", json={})
    assert response.status_code == 403
    payload = response.json()
    assert "detail" not in payload
    assert payload["error"]["code"] == "csrf_failed"


def test_config_apply_calls_apply_callback() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_apply"] = True

    call_count = 0
    received_actor: dict | None = None

    class ApplyAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0",
                )
            )

        def apply_config_candidate(
            self,
            candidate: dict,
            expected_hash: str | None = None,
            actor: dict | None = None,
        ) -> Any:
            nonlocal call_count, received_actor
            call_count += 1
            received_actor = actor
            return ok_result({"applied": True})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self,
            run_id: str,
            artifact_id: str,
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=ApplyAdapter())
    client = TestClient(app)
    _login(client)

    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/apply",
        json={"key": "value"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    assert call_count == 1, "Apply callback was not called"
    assert received_actor is not None
    assert "user_id" in received_actor
    assert "role" in received_actor


def test_config_apply_without_adapter_method_returns_501() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_apply"] = True

    class NoApplyAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0",
                )
            )

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=NoApplyAdapter())
    client = TestClient(app)
    _login(client)

    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/apply",
        json={},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 501, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "feature_unavailable"


def test_auth_failure_does_not_call_validate_or_apply() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True
    settings["features"]["config_apply"] = True

    validate_called = False
    apply_called = False

    class GuardedAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(
                    product_id="test",
                    title="Test",
                    version="1.0",
                )
            )

        def validate_config_candidate(
            self, candidate: dict
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal validate_called
            validate_called = True
            return ok_result({})

        def apply_config_candidate(
            self,
            candidate: dict,
            expected_hash: str | None = None,
            actor: dict | None = None,
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal apply_called
            apply_called = True
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=GuardedAdapter())
    client = TestClient(app)

    client.post("/api/config/preview", json={})
    client.post("/api/config/apply", json={})

    assert not validate_called, "validate_config_candidate called without auth"
    assert not apply_called, "apply_config_candidate called without auth"


def test_action_execute_receives_actor() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    received_actor: dict | None = None

    class ActionActorAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def execute_action(
            self,
            action_id: str,
            payload: dict,
            actor: dict | None = None,
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal received_actor
            received_actor = actor
            return ok_result({"executed": True})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=ActionActorAdapter())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)

    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/actions/execute",
        json={"action_id": "test", "payload": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    assert received_actor is not None, "Actor was not passed to execute_action"
    assert "user_id" in received_actor
    assert "role" in received_actor


def test_token_comparison_uses_hmac() -> None:
    service = AuthService(_make_auth_settings(enabled=True))
    assert service._resolve_role(_TEST_ADMIN_TOKEN) == UserRole.admin
    assert service._resolve_role(_TEST_OPERATOR_TOKEN) == UserRole.operator
    assert service._resolve_role(_TEST_ADMIN_TOKEN.upper()) is None
    assert service._resolve_role("") is None


def test_config_preview_without_adapter_method_returns_501() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    class NoValidateAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=NoValidateAdapter())
    client = TestClient(app)
    _login(client)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]
    response = client.post(
        "/api/config/preview",
        json={},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 501, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "feature_unavailable"


def test_action_preview_without_adapter_method_returns_501() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    class NoPreviewAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=NoPreviewAdapter())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]
    response = client.post(
        "/api/actions/preview",
        json={"action_id": "test", "payload": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 501, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "feature_unavailable"


def test_action_execute_without_adapter_method_returns_501() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    class NoExecAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=NoExecAdapter())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]
    response = client.post(
        "/api/actions/execute",
        json={"action_id": "test", "payload": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 501, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "feature_unavailable"


def test_config_apply_passes_expected_hash_and_actor() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_apply"] = True

    received: dict = {}

    class HashActorAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def apply_config_candidate(
            self,
            candidate: dict,
            expected_hash: str | None = None,
            actor: dict | None = None,
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal received
            received = {
                "candidate": candidate,
                "expected_hash": expected_hash,
                "actor": actor,
            }
            return ok_result({"applied": True})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=HashActorAdapter())
    client = TestClient(app)
    _login(client)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/apply",
        json={
            "candidate": {"key": "value"},
            "expected_hash": "abc123",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    assert received.get("candidate") == {"key": "value"}
    assert received.get("expected_hash") == "abc123"
    assert received.get("actor") is not None
    assert "user_id" in received["actor"]
    assert "role" in received["actor"]


def test_config_preview_unwraps_candidate() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    received_candidate: Any = None

    class UnwrapAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def validate_config_candidate(
            self, candidate: dict
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal received_candidate
            received_candidate = candidate
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=UnwrapAdapter())
    client = TestClient(app)
    _login(client)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/preview",
        json={"candidate": {"key": "value"}, "extra": "ignored"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
    assert received_candidate == {"key": "value"}, (
        f"Expected candidate={{'key': 'value'}}, got {received_candidate}"
    )


def test_config_preview_rejects_non_object_body() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    call_count: int = 0

    class TrackAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def validate_config_candidate(
            self, candidate: dict
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=TrackAdapter())
    client = TestClient(app)
    _login(client)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/preview",
        content=b'["not", "an", "object"]',
        headers={
            "X-CSRF-Token": csrf_token,
            "Content-Type": "application/json",
        },
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"
    assert call_count == 0, "Adapter callback must not be called"


def test_config_apply_rejects_non_object_candidate() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_apply"] = True

    call_count: int = 0

    class TrackApplyAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def apply_config_candidate(
            self,
            candidate: dict,
            expected_hash: str | None = None,
            actor: dict | None = None,
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=TrackApplyAdapter())
    client = TestClient(app)
    _login(client)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/apply",
        json={"candidate": ["not", "a", "dict"]},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"
    assert call_count == 0, "Adapter callback must not be called"


def test_config_apply_rejects_non_string_expected_hash() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_apply"] = True

    call_count: int = 0

    class HashCheckAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def apply_config_candidate(
            self,
            candidate: dict,
            expected_hash: str | None = None,
            actor: dict | None = None,
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=HashCheckAdapter())
    client = TestClient(app)
    _login(client)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/apply",
        json={"candidate": {}, "expected_hash": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"
    assert call_count == 0, "Adapter callback must not be called"


def test_action_preview_rejects_missing_action_id() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    call_count: int = 0

    class TrackPreviewAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def preview_action(
            self, action_id: str, payload: dict
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=TrackPreviewAdapter())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/actions/preview",
        json={"payload": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"
    assert call_count == 0, "Adapter callback must not be called"


def test_action_preview_rejects_non_string_action_id() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    call_count: int = 0

    class TrackPreviewAdapter2(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def preview_action(
            self, action_id: str, payload: dict
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=TrackPreviewAdapter2())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/actions/preview",
        json={"action_id": 123, "payload": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"
    assert call_count == 0, "Adapter callback must not be called"


def test_action_preview_rejects_non_object_payload() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    call_count: int = 0

    class TrackPreviewAdapter3(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def preview_action(
            self, action_id: str, payload: dict
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=TrackPreviewAdapter3())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/actions/preview",
        json={"action_id": "test", "payload": ["not", "a", "dict"]},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"
    assert call_count == 0, "Adapter callback must not be called"


def test_action_execute_rejects_non_object_payload() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    call_count: int = 0

    class TrackExecAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def execute_action(
            self, action_id: str, payload: dict, actor: dict | None = None
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=TrackExecAdapter())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/actions/execute",
        json={"action_id": "test", "payload": ["not", "a", "dict"]},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 400, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"
    assert call_count == 0, "Adapter callback must not be called"


def test_preview_success_envelope_is_read_only() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    class PreviewROAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def validate_config_candidate(
            self, candidate: dict
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({"preview": True})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=PreviewROAdapter())
    client = TestClient(app)
    _login(client)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/config/preview",
        json={"candidate": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True, "Preview envelope must be read_only=true"


def test_execute_success_envelope_is_not_read_only() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["operator_actions"] = True

    class ExecROAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def execute_action(
            self, action_id: str, payload: dict, actor: dict | None = None
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({"executed": True})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=ExecROAdapter())
    client = TestClient(app)
    _login(client, token=_TEST_OPERATOR_TOKEN)
    csrf_resp = client.get("/auth/csrf")
    csrf_token = csrf_resp.json()["data"]["csrf_token"]

    response = client.post(
        "/api/actions/execute",
        json={"action_id": "test", "payload": {}},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is False, "Execute envelope must be read_only=false"


def test_auth_enabled_requires_cookie_secure() -> None:
    from beeui_module.core.settings import _validate_auth

    with pytest.raises(ValueError, match="cookie_secure"):
        _validate_auth(
            {
                "auth": {
                    "enabled": True,
                    "session_secret": "s",
                    "operator_token": "o",
                    "admin_token": "a",
                }
            }
        )


def test_auth_cookie_secure_flag_false_for_local() -> None:
    settings = load_settings(settings_path())
    settings["auth"]["enabled"] = True
    settings["auth"]["session_secret"] = _TEST_SECRET
    settings["auth"]["operator_token"] = _TEST_OPERATOR_TOKEN
    settings["auth"]["admin_token"] = _TEST_ADMIN_TOKEN
    settings["auth"]["cookie_secure"] = False

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    response = client.post(
        "/auth/login",
        data={"user_id": "admin", "token": _TEST_ADMIN_TOKEN},
        follow_redirects=False,
    )
    assert response.status_code == 302
    set_cookie = response.headers.get("set-cookie", "")
    assert "Secure" not in set_cookie, f"Cookie should not be Secure: {set_cookie}"
    assert session_cookie_name() in set_cookie


def test_auth_cookie_secure_flag_true_sets_secure_cookie() -> None:
    settings = load_settings(settings_path())
    settings["auth"]["enabled"] = True
    settings["auth"]["session_secret"] = _TEST_SECRET
    settings["auth"]["operator_token"] = _TEST_OPERATOR_TOKEN
    settings["auth"]["admin_token"] = _TEST_ADMIN_TOKEN
    settings["auth"]["cookie_secure"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    response = client.post(
        "/auth/login",
        data={"user_id": "admin", "token": _TEST_ADMIN_TOKEN},
        follow_redirects=False,
    )
    assert response.status_code == 302
    set_cookie = response.headers.get("set-cookie", "")
    assert "Secure" in set_cookie, f"Cookie should be Secure: {set_cookie}"
    assert session_cookie_name() in set_cookie


def test_security_headers_on_html_route() -> None:
    app = create_beeui_app()
    client = TestClient(app)
    response = client.get("/")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_security_headers_on_auth_route() -> None:
    settings = load_settings(settings_path())
    settings["auth"]["enabled"] = True
    settings["auth"]["session_secret"] = _TEST_SECRET
    settings["auth"]["operator_token"] = _TEST_OPERATOR_TOKEN
    settings["auth"]["admin_token"] = _TEST_ADMIN_TOKEN
    settings["auth"]["cookie_secure"] = False

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_auth_csrf_route_is_no_store() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    _login(client)

    response = client.get("/auth/csrf")

    assert response.status_code == 200
    assert response.headers.get("Cache-Control") == "no-store"


def test_security_headers_on_api_error() -> None:
    settings = load_settings(settings_path())
    settings["auth"]["enabled"] = True
    settings["auth"]["session_secret"] = _TEST_SECRET
    settings["auth"]["operator_token"] = _TEST_OPERATOR_TOKEN
    settings["auth"]["admin_token"] = _TEST_ADMIN_TOKEN
    settings["auth"]["cookie_secure"] = False
    settings["features"]["config_preview"] = True

    app = create_beeui_app(settings=settings)
    client = TestClient(app)
    response = client.post("/api/config/preview", json={})
    assert response.status_code == 401
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


def test_auth_routes_follow_route_prefix() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["web"]["route_prefix"] = "/bee"

    app = create_beeui_app(settings=settings)
    client = TestClient(app)

    response = client.get("/bee/auth/login")
    assert response.status_code == 200
    assert "Sign in" in response.text

    response = client.post(
        "/bee/auth/login",
        data={"user_id": "admin", "token": _TEST_ADMIN_TOKEN},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert session_cookie_name() in response.cookies


def test_invalid_csrf_does_not_call_adapter() -> None:
    settings = load_settings(settings_path())
    settings["auth"] = _make_auth_settings(enabled=True)
    settings["features"]["config_preview"] = True

    call_count: int = 0

    class GuardAdapter(ProductUiAdapterBase):
        def __init__(self) -> None:
            super().__init__(
                AdapterMetadata(product_id="test", title="Test", version="1.0")
            )

        def validate_config_candidate(
            self, candidate: dict
        ) -> AdapterResult | AdapterErrorResult:
            nonlocal call_count
            call_count += 1
            return ok_result({})

        def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def list_runs(self) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result({"id": run_id})

        def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
            return ok_result([])

        def read_artifact(
            self, run_id: str, artifact_id: str
        ) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

        def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
            return ok_result({})

    app = create_beeui_app(settings=settings, adapter=GuardAdapter())
    client = TestClient(app)
    _login(client)

    response = client.post(
        "/api/config/preview",
        json={"candidate": {}},
        headers={"X-CSRF-Token": "invalid-csrf-token"},
    )
    assert response.status_code == 403, f"Got {response.status_code}: {response.text}"
    payload = response.json()
    assert payload["error"]["code"] == "csrf_failed"
    assert call_count == 0, "Adapter callback must not be called with invalid CSRF"


def test_validate_auth_does_not_mutate_env_refs() -> None:
    import os

    from beeui_module.core.settings import _validate_auth

    os.environ["TEST_AUTH_SECRET"] = "resolved-secret"
    os.environ["TEST_AUTH_OP"] = "resolved-op"
    os.environ["TEST_AUTH_ADMIN"] = "resolved-admin"
    try:
        auth_cfg = {
            "enabled": True,
            "cookie_secure": False,
            "session_secret": "${TEST_AUTH_SECRET}",
            "operator_token": "${TEST_AUTH_OP}",
            "admin_token": "${TEST_AUTH_ADMIN}",
        }
        settings = {"auth": auth_cfg}
        _validate_auth(settings)

        assert auth_cfg["session_secret"] == "${TEST_AUTH_SECRET}", (
            f"Expected original env ref, got: {auth_cfg['session_secret']}"
        )
        assert auth_cfg["operator_token"] == "${TEST_AUTH_OP}"
        assert auth_cfg["admin_token"] == "${TEST_AUTH_ADMIN}"
    finally:
        del os.environ["TEST_AUTH_SECRET"]
        del os.environ["TEST_AUTH_OP"]
        del os.environ["TEST_AUTH_ADMIN"]
