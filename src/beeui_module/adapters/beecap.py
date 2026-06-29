from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from beeui_module.adapters.base import ProductUiAdapterBase
from beeui_module.adapters.envelopes import (
    AdapterErrorResult,
    AdapterMetadata,
    AdapterResult,
    AdapterWarning,
    error_result_from_exception,
    ok_result,
    partial_result,
)
from beeui_module.adapters.errors import NotFoundError
from beeui_module.adapters.ids import validate_artifact_id, validate_run_id


class BeeCapFixtureAdapter(ProductUiAdapterBase):
    def __init__(self, fixture_root: Path | None = None) -> None:
        metadata = AdapterMetadata(
            product_id="beecap",
            title="BeeCap",
            version="0.1.0",
            capabilities=("dashboard", "runs", "artifacts"),
            supported_pages=("/", "/runs"),
        )
        super().__init__(metadata)
        self._fixture_root = fixture_root
        self._dashboard_data: dict[str, Any] | None = None
        self._runs_data: list[dict[str, Any]] | None = None
        self._artifacts_data: dict[str, Any] | None = None

    def _load_yaml(self, filename: str) -> dict[str, Any]:
        """Load a YAML fixture file from the configured root."""
        if self._fixture_root is None:
            return {}
        path = self._fixture_root / filename
        if not path.is_file():
            return {}
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def _get_dashboard_data(self) -> dict[str, Any]:
        if self._dashboard_data is None:
            self._dashboard_data = self._load_yaml("dashboard.yml")
        return self._dashboard_data

    def _get_runs_data(self) -> list[dict[str, Any]]:
        runs_data = self._runs_data
        if runs_data is None:
            raw = self._load_yaml("runs.yml")
            loaded_runs = raw.get("runs", [])
            runs_data = loaded_runs if isinstance(loaded_runs, list) else []
            self._runs_data = runs_data
        return runs_data

    def _get_artifacts_data(self) -> dict[str, Any]:
        artifacts_data = self._artifacts_data
        if artifacts_data is None:
            raw = self._load_yaml("artifacts.yml")
            loaded_artifacts = raw.get("artifacts", {})
            artifacts_data = (
                loaded_artifacts if isinstance(loaded_artifacts, dict) else {}
            )
            self._artifacts_data = artifacts_data
        return artifacts_data

    def get_dashboard(self) -> AdapterResult | AdapterErrorResult:
        try:
            data = self._get_dashboard_data()
            if not data:
                return ok_result(
                    {"latest_run": None, "summary": {}, "kpi_items": []},
                    meta={"product": "beecap", "source": "fixture"},
                )

            warnings: list[AdapterWarning] = []
            latest_run = data.get("latest_run")
            summary = data.get("summary", {})

            if latest_run is None:
                warnings.append(
                    AdapterWarning(
                        code="no_latest_run",
                        message="No latest run available",
                    )
                )
            mrkt = summary.get("mrkt")
            if mrkt is None:
                warnings.append(
                    AdapterWarning(
                        code="mrkt_unavailable",
                        message="MRKT summary data is unavailable",
                    )
                )
            binance = summary.get("binance")
            if binance is None:
                warnings.append(
                    AdapterWarning(
                        code="binance_unavailable",
                        message="Binance summary data is unavailable",
                    )
                )

            if warnings:
                return partial_result(
                    data=deepcopy(data),
                    warnings=warnings,
                    meta={"product": "beecap", "source": "fixture"},
                )

            return ok_result(
                deepcopy(data),
                meta={"product": "beecap", "source": "fixture"},
            )
        except Exception as exc:
            return error_result_from_exception(exc)

    def list_runs(self) -> AdapterResult | AdapterErrorResult:
        try:
            runs = self._get_runs_data()
            summaries = [{"id": run["id"], "status": run["status"]} for run in runs]
            return ok_result(
                deepcopy(summaries),
                meta={"count": len(summaries), "product": "beecap"},
            )
        except Exception as exc:
            return error_result_from_exception(exc)

    def get_run(self, run_id: str) -> AdapterResult | AdapterErrorResult:
        try:
            safe_id = validate_run_id(run_id)
            runs = self._get_runs_data()
            for run in runs:
                if run["id"] == safe_id:
                    payload = {
                        "id": run["id"],
                        "status": run["status"],
                        "started_at": run.get("started_at"),
                        "completed_at": run.get("completed_at"),
                        "artifacts": [
                            {
                                "artifact_id": a["artifact_id"],
                                "content_type": a["content_type"],
                            }
                            for a in run.get("artifacts", [])
                        ],
                    }
                    return ok_result(
                        deepcopy(payload),
                        meta={"product": "beecap"},
                    )
            raise NotFoundError(f"Run not found: {safe_id}")
        except Exception as exc:
            return error_result_from_exception(exc)

    def list_artifacts(self, run_id: str) -> AdapterResult | AdapterErrorResult:
        try:
            safe_id = validate_run_id(run_id)
            runs = self._get_runs_data()
            for run in runs:
                if run["id"] == safe_id:
                    artifacts = [
                        {
                            "artifact_id": a["artifact_id"],
                            "content_type": a["content_type"],
                        }
                        for a in run.get("artifacts", [])
                    ]
                    return ok_result(
                        deepcopy(artifacts),
                        meta={"product": "beecap", "run_id": safe_id},
                    )
            raise NotFoundError(f"Run not found: {safe_id}")
        except Exception as exc:
            return error_result_from_exception(exc)

    def read_artifact(
        self, run_id: str, artifact_id: str
    ) -> AdapterResult | AdapterErrorResult:
        try:
            safe_run_id = validate_run_id(run_id)
            safe_artifact_id = validate_artifact_id(artifact_id)

            runs = self._get_runs_data()
            run = next((item for item in runs if item["id"] == safe_run_id), None)
            if run is None:
                raise NotFoundError(f"Run not found: {safe_run_id}")

            allowed_artifact_ids = {
                item["artifact_id"] for item in run.get("artifacts", [])
            }
            if safe_artifact_id not in allowed_artifact_ids:
                raise NotFoundError(
                    f"Artifact not found: {safe_artifact_id} for run {safe_run_id}"
                )

            artifacts = self._get_artifacts_data()
            artifact = artifacts.get(safe_artifact_id)
            if artifact is None:
                raise NotFoundError(
                    f"Artifact not found: {safe_artifact_id} for run {safe_run_id}"
                )

            if artifact.get("_corrupted"):
                return partial_result(
                    data={
                        "artifact_id": safe_artifact_id,
                        "content_type": artifact.get("content_type", "unknown"),
                        "content": None,
                    },
                    warnings=[
                        AdapterWarning(
                            code="artifact_corrupted",
                            message=f"Artifact {safe_artifact_id} appears corrupted or unreadable",
                        )
                    ],
                    meta={"product": "beecap", "run_id": safe_run_id},
                )

            return ok_result(
                deepcopy(
                    {
                        "artifact_id": safe_artifact_id,
                        "content_type": artifact.get("content_type", "unknown"),
                        "content": artifact.get("content"),
                    }
                ),
                meta={"product": "beecap", "run_id": safe_run_id},
            )
        except Exception as exc:
            return error_result_from_exception(exc)

    def get_config_read_model(self) -> AdapterResult | AdapterErrorResult:
        return ok_result(
            {
                "product": "beecap",
                "mode": "fixture",
                "read_only": True,
                "editable": False,
            },
            meta={"product": "beecap"},
        )
