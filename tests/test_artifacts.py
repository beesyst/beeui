from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from beeui_module.adapters.base import ProductUiAdapterBase
from beeui_module.adapters.envelopes import (
    AdapterErrorResult,
    AdapterMetadata,
    AdapterResult,
    error_result,
    ok_result,
)
from beeui_module.artifacts.preview import (
    MAX_CHARS_TEXT,
    MAX_JSON_BYTES,
    MAX_JSONL_ROWS,
    build_preview,
)
from beeui_module.artifacts.redaction import redact_text, redact_value
from beeui_module.web.app import create_beeui_app

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "beecap"


# Класс: адаптер для тестирования артефактов с фикстурами
class ArtifactTestAdapter(ProductUiAdapterBase):
    def __init__(self) -> None:
        super().__init__(
            AdapterMetadata(
                product_id="test",
                title="Test Artifacts",
                version="0.1.0",
                capabilities=("artifacts",),
                supported_pages=(),
            )
        )

    def get_dashboard(self) -> AdapterResult:
        return ok_result({})

    def list_runs(self) -> AdapterResult:
        return ok_result([{"id": "run_test_001", "status": "ok"}])

    def get_run(self, run_id: str) -> AdapterResult:
        return ok_result({"id": run_id, "status": "ok"})

    def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
        if run_id == "run_test_001":
            return ok_result(
                [
                    {"artifact_id": "report_json", "content_type": "application/json"},
                    {"artifact_id": "data_jsonl", "content_type": "application/jsonl"},
                    {"artifact_id": "log_txt", "content_type": "text/plain"},
                    {
                        "artifact_id": "binary_file",
                        "content_type": "application/octet-stream",
                    },
                ]
            )
        if run_id == "run_no_artifacts":
            return ok_result([])
        return error_result("not_found", f"Run not found: {run_id}")

    def read_artifact(
        self,
        run_id: str,
        artifact_id: str,
    ) -> AdapterResult | AdapterErrorResult:
        if run_id != "run_test_001" and run_id != "run_large":
            return error_result("not_found", f"Artifact not found: {artifact_id}")

        artifacts = {
            "report_json": {
                "artifact_id": "report_json",
                "content_type": "application/json",
                "content": {"score": 0.95, "status": "ok", "count": 42},
            },
            "data_jsonl": {
                "artifact_id": "data_jsonl",
                "content_type": "application/jsonl",
                "content": [
                    {"id": 1, "event": "start"},
                    {"id": 2, "event": "process"},
                    {"id": 3, "event": "complete"},
                ],
            },
            "log_txt": {
                "artifact_id": "log_txt",
                "content_type": "text/plain",
                "content": "Run completed successfully.\nAll systems operational.",
            },
            "binary_file": {
                "artifact_id": "binary_file",
                "content_type": "application/octet-stream",
                "content": b"\x00\x01\x02\x03",
            },
            "malformed_json": {
                "artifact_id": "malformed_json",
                "content_type": "application/json",
                "content": "{invalid json content",
            },
            "malformed_jsonl": {
                "artifact_id": "malformed_jsonl",
                "content_type": "application/jsonl",
                "content": '{"id": 1}\ninvalid line\n{"id": 3}',
            },
            "large_json": {
                "artifact_id": "large_json",
                "content_type": "application/json",
                "content": "x" * (MAX_JSON_BYTES + 1),
            },
            "large_text": {
                "artifact_id": "large_text",
                "content_type": "text/plain",
                "content": "x" * (MAX_CHARS_TEXT + 1000),
            },
        }

        artifact = artifacts.get(artifact_id)
        if artifact is None:
            return error_result("not_found", f"Artifact not found: {artifact_id}")

        return ok_result(artifact)

    def get_config_read_model(self) -> AdapterResult:
        return ok_result({"mode": "test", "read_only": True})


# Класс: тесты для редакции и превью артефактов, а также маршрутов без адаптера и с префиксом
class TestRedaction:
    def test_redact_sensitive_keys(self) -> None:
        data = {
            "api_key": "sk-1234",
            "token": "abc",
            "password": "secret",
            "safe_field": "hello",
            "nested": {"api_secret": "xyz", "name": "test"},
        }
        redacted = redact_value(data)
        assert redacted["api_key"] == "*** REDACTED ***"
        assert redacted["safe_field"] == "hello"
        assert redacted["nested"]["api_secret"] == "*** REDACTED ***"
        assert redacted["nested"]["name"] == "test"

    def test_redact_list(self) -> None:
        data = [{"token": "abc"}, {"name": "hello"}]
        redacted = redact_value(data)
        assert redacted[0]["token"] == "*** REDACTED ***"
        assert redacted[1]["name"] == "hello"

    def test_redact_text(self) -> None:
        text = "api_key = sk-1234\ntoken = abc\nnormal line"
        result = redact_text(text)
        lines = result.splitlines()
        assert "*** REDACTED ***" in lines[0]
        assert "*** REDACTED ***" in lines[1]
        assert lines[2] == "normal line"

    def test_redact_primitive(self) -> None:
        assert redact_value("hello") == "hello"
        assert redact_value(42) == 42
        assert redact_value(None) is None


# Класс: тесты для превью артефактов с различными типами контента и ошибками
class TestPreviewJson:
    def test_json_preview_dict(self) -> None:
        preview = build_preview("test", "application/json", {"key": "value"})
        assert preview.preview_type == "json"
        assert preview.preview_data == {"key": "value"}
        assert not preview.metadata_only

    def test_json_preview_list(self) -> None:
        preview = build_preview("test", "application/json", [1, 2, 3])
        assert preview.preview_type == "json"
        assert preview.preview_data == [1, 2, 3]

    def test_json_preview_string(self) -> None:
        preview = build_preview("test", "application/json", '{"a": 1}')
        assert preview.preview_type == "json"
        assert preview.preview_data == {"a": 1}

    def test_json_malformed(self) -> None:
        preview = build_preview("test", "application/json", "{broken")
        assert preview.preview_type == "json"
        assert preview.error is not None
        assert "malformed" in preview.error.lower() or "Malformed" in preview.error
        assert preview.metadata_only

    def test_json_null_content(self) -> None:
        preview = build_preview("test", "application/json", None)
        assert preview.metadata_only
        assert preview.preview_data is None

    def test_json_large_content(self) -> None:
        large = "x" * (MAX_JSON_BYTES + 1)
        preview = build_preview("test", "application/json", large)
        assert preview.metadata_only
        assert preview.error is not None
        assert "exceeds maximum" in preview.error.lower()


# Класс: тесты для превью артефактов с типом application/jsonl, включая обработку ошибок и больших данных
class TestPreviewJsonl:
    def test_jsonl_preview_list(self) -> None:
        preview = build_preview("test", "application/jsonl", [{"a": 1}, {"b": 2}])
        assert preview.preview_type == "jsonl"
        assert len(preview.preview_data) == 2
        assert not preview.metadata_only

    def test_jsonl_preview_string(self) -> None:
        data = '{"id": 1}\n{"id": 2}\n{"id": 3}'
        preview = build_preview("test", "application/jsonl", data)
        assert preview.preview_type == "jsonl"
        assert len(preview.preview_data) == 3
        assert preview.row_count == 3

    def test_jsonl_malformed_rows(self) -> None:
        data = '{"id": 1}\nbroken\n{"id": 3}'
        preview = build_preview("test", "application/jsonl", data)
        assert preview.preview_type == "jsonl"
        assert len(preview.row_warnings) > 0
        assert "malformed" in preview.row_warnings[0].lower()
        assert len(preview.preview_data) == 2  # valid rows only

    def test_jsonl_large_content(self) -> None:
        large = "x" * (MAX_JSON_BYTES + 1)
        preview = build_preview("test", "application/jsonl", large)
        assert preview.metadata_only
        assert preview.error is not None

    def test_jsonl_truncated(self) -> None:
        rows = [{"id": i} for i in range(MAX_JSONL_ROWS + 100)]
        preview = build_preview("test", "application/jsonl", rows)
        assert preview.truncated
        assert len(preview.preview_data) == MAX_JSONL_ROWS


# Класс: тесты для превью текстовых артефактов, включая проверку редактирования и обрезки больших данных
class TestPreviewText:
    def test_text_preview(self) -> None:
        preview = build_preview("test", "text/plain", "hello world")
        assert preview.preview_type == "text"
        assert preview.preview_data == "hello world"
        assert not preview.metadata_only

    def test_text_preview_redacts_sensitive_lines(self) -> None:
        preview = build_preview("test", "text/plain", "api_key = sk-1234\nnormal line")
        assert preview.preview_type == "text"
        assert "*** REDACTED ***" in preview.preview_data
        assert "sk-1234" not in preview.preview_data
        assert "normal line" in preview.preview_data

    def test_text_truncated(self) -> None:
        large = "x" * (MAX_CHARS_TEXT + 100)
        preview = build_preview("test", "text/plain", large)
        assert preview.truncated
        assert len(preview.preview_data) == MAX_CHARS_TEXT

    def test_text_null_content(self) -> None:
        preview = build_preview("test", "text/plain", None)
        assert preview.metadata_only
        assert preview.preview_data is None


# Класс: тест для превью артефактов с неподдерживаемым типом контента, проверяющий, что возвращается только метадата без данных
class TestPreviewUnsupported:
    def test_binary_metadata_only(self) -> None:
        preview = build_preview("test", "application/octet-stream", b"\x00\x01")
        assert preview.preview_type == "unsupported"
        assert preview.metadata_only
        assert preview.preview_data is None


# Класс: тесты для маршрутов артефактов без адаптера, с префиксом и для проверки безопасности, включая отсутствие мутации данных и экранирование HTML
class TestArtifactRoutes:
    def _make_app(self, adapter: Any = None) -> FastAPI:
        return create_beeui_app(
            adapter=adapter,
        )

    def test_html_list_returns_200(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/runs/run_test_001/artifacts")
        assert resp.status_code == 200
        assert "report_json" in resp.text
        assert "application/json" in resp.text

    def test_html_list_empty(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/runs/run_no_artifacts/artifacts")
        assert resp.status_code == 200
        assert "No artifacts" in resp.text

    def test_html_list_run_not_found(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/runs/nonexistent/artifacts")
        assert resp.status_code == 200
        assert "Error" in resp.text or "not found" in resp.text.lower()

    def test_html_list_invalid_run_id(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        # Use run_id with semicolon (invalid per validate_run_id)
        resp = client.get("/runs/run;id/artifacts")
        assert resp.status_code == 400

    def test_html_detail_json(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/runs/run_test_001/artifacts/report_json")
        assert resp.status_code == 200
        assert "report_json" in resp.text

    def test_html_detail_text(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/runs/run_test_001/artifacts/log_txt")
        assert resp.status_code == 200
        assert "completed successfully" in resp.text

    def test_html_detail_invalid_artifact_id(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/runs/run_test_001/artifacts/artifact;id")
        assert resp.status_code == 400

    def test_html_detail_invalid_run_id(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/runs/%3B/artifacts/test")  # ; encoded - goes through as %3B
        assert resp.status_code == 400

    def test_api_list_returns_json(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert len(data["data"]) == 4

    def test_adapter_list_invalid_artifact_id_is_not_rendered_or_returned(self) -> None:
        adapter = ArtifactTestAdapter()

        def patched_list_artifacts(run_id: str):
            return ok_result(
                [
                    {"artifact_id": "safe_report", "content_type": "text/plain"},
                    {"artifact_id": "../unsafe", "content_type": "text/plain"},
                    {"artifact_id": None, "content_type": "text/plain"},
                    "broken",
                ]
            )

        adapter.list_artifacts = patched_list_artifacts

        app = self._make_app(adapter)
        client = TestClient(app)

        html_resp = client.get("/runs/run_test_001/artifacts")
        assert html_resp.status_code == 200
        assert "safe_report" in html_resp.text
        assert "../unsafe" not in html_resp.text
        assert "/runs/run_test_001/artifacts/../unsafe" not in html_resp.text

        api_resp = client.get("/api/runs/run_test_001/artifacts")
        assert api_resp.status_code == 200
        data = api_resp.json()
        assert data["data"] == [
            {"artifact_id": "safe_report", "content_type": "text/plain"}
        ]
        assert {warning["code"] for warning in data["warnings"]} == {
            "invalid_artifact_id",
            "malformed_artifact_item",
        }

    def test_api_list_invalid_run_id(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run;id/artifacts")
        assert resp.status_code == 400

    def test_api_detail_returns_json(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/report_json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["data"]["preview_type"] == "json"
        assert data["data"]["artifact_id"] == "report_json"

    def test_adapter_detail_artifact_id_does_not_override_route_param(self) -> None:
        adapter = ArtifactTestAdapter()

        def patched_read_artifact(run_id: str, artifact_id: str):
            return ok_result(
                {
                    "artifact_id": "../unsafe",
                    "content_type": "application/json",
                    "content": {"ok": True},
                }
            )

        adapter.read_artifact = patched_read_artifact

        app = self._make_app(adapter)
        client = TestClient(app)

        api_resp = client.get("/api/runs/run_test_001/artifacts/report_json")
        assert api_resp.status_code == 200
        assert api_resp.json()["data"]["artifact_id"] == "report_json"

        html_resp = client.get("/runs/run_test_001/artifacts/report_json")
        assert html_resp.status_code == 200
        assert "Artifact: report_json" in html_resp.text
        assert "../unsafe" not in html_resp.text

    def test_api_detail_text(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/log_txt")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["data"]["preview_type"] == "text"
        assert "completed successfully" in data["data"]["preview_data"]

    def test_api_detail_unsupported(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/binary_file")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["preview_type"] == "unsupported"
        assert data["data"]["metadata_only"] is True

    def test_api_detail_invalid_ids(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run;id/artifacts/bad")
        assert resp.status_code == 400

        resp2 = client.get("/api/runs/run_test_001/artifacts/artifact;id")
        assert resp2.status_code == 400

    def test_api_detail_not_found(self) -> None:
        adapter = ArtifactTestAdapter()
        app = self._make_app(adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/nonexistent")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "not_found"


# Класс: тесты для маршрутов артефактов без адаптера, с префиксом и для проверки безопасности, включая отсутствие мутации данных и экранирование HTML
class TestArtifactRoutesNoAdapter:
    def _make_app(self) -> FastAPI:
        return create_beeui_app()

    def test_html_list_adapter_unavailable(self) -> None:
        app = self._make_app()
        client = TestClient(app)
        resp = client.get("/runs/run_test_001/artifacts")
        assert resp.status_code == 503
        assert "Adapter" in resp.text

    def test_html_detail_adapter_unavailable(self) -> None:
        app = self._make_app()
        client = TestClient(app)
        resp = client.get("/runs/run_test_001/artifacts/report_json")
        assert resp.status_code == 503
        assert "Adapter" in resp.text

    def test_api_list_adapter_unavailable(self) -> None:
        app = self._make_app()
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts")
        assert resp.status_code == 503
        data = resp.json()
        assert data["error"]["code"] == "adapter_unavailable"

    def test_api_detail_adapter_unavailable(self) -> None:
        app = self._make_app()
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/report_json")
        assert resp.status_code == 503
        data = resp.json()
        assert data["error"]["code"] == "adapter_unavailable"


# Класс: тесты для маршрутов артефактов с префиксом, проверяющие, что маршруты работают корректно с заданным префиксом и возвращают ожидаемые данные
class TestArtifactRoutesWithPrefix:
    def test_route_prefix_works(self) -> None:
        from beeui_module.core.paths import settings_path
        from beeui_module.core.settings import load_settings

        settings = load_settings(settings_path())
        settings["web"]["route_prefix"] = "/bee"

        adapter = ArtifactTestAdapter()
        app = create_beeui_app(settings=settings, adapter=adapter)
        client = TestClient(app)

        resp = client.get("/bee/runs/run_test_001/artifacts")
        assert resp.status_code == 200
        assert "report_json" in resp.text

        resp2 = client.get("/bee/api/runs/run_test_001/artifacts")
        assert resp2.status_code == 200
        data = resp2.json()
        assert data["status"] == "ok"


# Класс: тесты для превью артефактов с различными типами контента и ошибками
class TestArtifactPreviewViaRoute:
    def test_malformed_json_via_route(self) -> None:
        adapter = ArtifactTestAdapter()
        app = create_beeui_app(adapter=adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/malformed_json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["data"]["preview_type"] == "json"
        assert data["data"]["error"] is not None
        assert data["data"]["metadata_only"] is True

    def test_malformed_jsonl_via_route(self) -> None:
        adapter = ArtifactTestAdapter()
        app = create_beeui_app(adapter=adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/malformed_jsonl")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["data"]["preview_type"] == "jsonl"
        assert len(data["data"]["row_warnings"]) > 0

    def test_large_text_truncated_via_route(self) -> None:
        adapter = ArtifactTestAdapter()
        app = create_beeui_app(adapter=adapter)
        client = TestClient(app)
        resp = client.get("/api/runs/run_test_001/artifacts/large_text")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["truncated"] is True
        assert data["data"]["preview_type"] == "text"


# Класс: тесты для маршрутов артефактов без адаптера, с префиксом и для проверки безопасности, включая отсутствие мутации данных и экранирование HTML
class TestArtifactSecurity:
    def test_no_mutation_of_source_data(self) -> None:
        """Verify that artifact routes do not mutate source fixture files."""
        adapter = ArtifactTestAdapter()
        app = create_beeui_app(adapter=adapter)
        client = TestClient(app)

        resp1 = client.get("/api/runs/run_test_001/artifacts/report_json")
        resp2 = client.get("/api/runs/run_test_001/artifacts/report_json")

        assert resp1.json() == resp2.json()

    def test_html_escaping_in_text_preview(self) -> None:
        adapter = ArtifactTestAdapter()

        original_read = adapter.read_artifact

        def patched_read(run_id: str, artifact_id: str):
            result = original_read(run_id, artifact_id)
            if artifact_id == "log_txt":
                return ok_result(
                    {
                        "artifact_id": "log_txt",
                        "content_type": "text/plain",
                        "content": "<script>alert(1)</script>",
                    }
                )
            return result

        adapter.read_artifact = patched_read

        app = create_beeui_app(adapter=adapter)
        client = TestClient(app)
        resp = client.get("/runs/run_test_001/artifacts/log_txt")

        assert resp.status_code == 200
        assert "&lt;script&gt;" in resp.text
        assert "<script>" not in resp.text

    def test_text_artifact_secret_redacted_in_html_and_api(self) -> None:
        adapter = ArtifactTestAdapter()

        original_read = adapter.read_artifact

        def patched_read(run_id: str, artifact_id: str):
            result = original_read(run_id, artifact_id)
            if artifact_id == "log_txt":
                return ok_result(
                    {
                        "artifact_id": "log_txt",
                        "content_type": "text/plain",
                        "content": "api_key = sk-1234\nnormal line",
                    }
                )
            return result

        adapter.read_artifact = patched_read

        app = create_beeui_app(adapter=adapter)
        client = TestClient(app)

        html_resp = client.get("/runs/run_test_001/artifacts/log_txt")
        assert html_resp.status_code == 200
        assert "*** REDACTED ***" in html_resp.text
        assert "sk-1234" not in html_resp.text
        assert "normal line" in html_resp.text

        api_resp = client.get("/api/runs/run_test_001/artifacts/log_txt")
        assert api_resp.status_code == 200
        data = api_resp.json()
        assert "*** REDACTED ***" in data["data"]["preview_data"]
        assert "sk-1234" not in data["data"]["preview_data"]
        assert "normal line" in data["data"]["preview_data"]

    def test_no_beecap_import(self) -> None:
        import sys

        for mod_name in ("beecap_module", "beeagent_module"):
            assert mod_name not in sys.modules

    def test_no_new_write_routes(self) -> None:
        from beeui_module.web.app import create_beeui_app

        adapter = ArtifactTestAdapter()
        app = create_beeui_app(adapter=adapter)

        for route in app.routes:
            methods = getattr(route, "methods", set()) or set()
            route_path = getattr(route, "path", "<unknown>")
            if methods and "GET" not in methods:
                raise AssertionError(
                    f"Unexpected non-GET route: {route_path} methods={methods}"
                )


# Класс: тест для чека, что маршруты артефактов не регистрируются, когда флаг features.browser_artifact отключен
class TestArtifactFeatureFlag:
    def test_artifact_routes_disabled_when_feature_flag_false(self) -> None:
        from beeui_module.core.paths import settings_path
        from beeui_module.core.settings import load_settings

        settings = load_settings(settings_path())
        settings["features"]["browser_artifact"] = False

        app = create_beeui_app(settings=settings, adapter=ArtifactTestAdapter())
        routes = {
            getattr(route, "path", "")
            for route in app.routes
            if isinstance(getattr(route, "path", None), str)
        }

        assert "/runs/{run_id}/artifacts" not in routes
        assert "/runs/{run_id}/artifacts/{artifact_id}" not in routes
        assert "/api/runs/{run_id}/artifacts" not in routes
        assert "/api/runs/{run_id}/artifacts/{artifact_id}" not in routes
