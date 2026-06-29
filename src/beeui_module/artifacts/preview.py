from __future__ import annotations

import json
from typing import Any

from beeui_module.artifacts.models import ArtifactPreview, PreviewType
from beeui_module.artifacts.redaction import redact_text, redact_value

MAX_JSON_BYTES = 512 * 1024
MAX_JSONL_ROWS = 500
MAX_CHARS_TEXT = 100_000


def _infer_preview_type(content_type: str, content: Any) -> PreviewType:
    ct = (content_type or "").lower()

    if "jsonl" in ct or "x-ndjson" in ct:
        return "jsonl"
    if "json" in ct:
        return "json"
    if isinstance(content, (dict, list)):
        return "json"
    if isinstance(content, str):
        stripped = content.strip()
        if stripped.startswith(("{", "[")) and stripped.endswith(("}", "]")):
            return "json"
        return "text"

    return "unsupported"


def _preview_json(content: Any) -> ArtifactPreview:
    preview_type: PreviewType = "json"

    if content is None:
        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=None,
            metadata_only=True,
        )

    raw: str | None = None
    if isinstance(content, str):
        raw = content
        if len(raw.encode("utf-8")) > MAX_JSON_BYTES:
            return ArtifactPreview(
                artifact_id="",
                content_type="",
                preview_type=preview_type,
                error="Content exceeds maximum preview size",
                metadata_only=True,
            )
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            return ArtifactPreview(
                artifact_id="",
                content_type="",
                preview_type=preview_type,
                error=f"Malformed JSON: {exc}",
                metadata_only=True,
            )
    elif isinstance(content, (dict, list)):
        parsed = content
        raw = json.dumps(parsed, ensure_ascii=False, indent=2, default=str)
        if len(raw.encode("utf-8")) > MAX_JSON_BYTES:
            return ArtifactPreview(
                artifact_id="",
                content_type="",
                preview_type=preview_type,
                error="Content exceeds maximum preview size after serialization",
                metadata_only=True,
            )
    else:
        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=None,
            metadata_only=True,
        )

    redacted = redact_value(parsed)
    return ArtifactPreview(
        artifact_id="",
        content_type="",
        preview_type=preview_type,
        preview_data=redacted,
    )


def _preview_jsonl(content: Any) -> ArtifactPreview:
    preview_type: PreviewType = "jsonl"

    if content is None:
        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=None,
            metadata_only=True,
        )

    rows: list[Any] = []
    row_warnings: list[str] = []

    if isinstance(content, list):
        for item in content:
            rows.append(redact_value(item))
            if len(rows) >= MAX_JSONL_ROWS:
                break
        truncated = len(content) > MAX_JSONL_ROWS

        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=rows,
            row_count=len(content),
            truncated=truncated,
        )

    if isinstance(content, str):
        raw = content
        if len(raw.encode("utf-8")) > MAX_JSON_BYTES:
            return ArtifactPreview(
                artifact_id="",
                content_type="",
                preview_type=preview_type,
                error="Content exceeds maximum preview size",
                metadata_only=True,
            )

        total_rows = 0
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            total_rows += 1
            if len(rows) >= MAX_JSONL_ROWS:
                continue
            try:
                parsed = json.loads(line)
                rows.append(redact_value(parsed))
            except (json.JSONDecodeError, ValueError) as exc:
                row_warnings.append(f"Row {total_rows}: malformed JSONL row ({exc})")

        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=rows,
            row_count=total_rows,
            truncated=total_rows > MAX_JSONL_ROWS,
            row_warnings=tuple(row_warnings),
        )

    return ArtifactPreview(
        artifact_id="",
        content_type="",
        preview_type=preview_type,
        preview_data=None,
        metadata_only=True,
    )


def _preview_text(content: Any) -> ArtifactPreview:
    preview_type: PreviewType = "text"

    if content is None:
        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=None,
            metadata_only=True,
        )

    if isinstance(content, str):
        if len(content) > MAX_CHARS_TEXT:
            truncated_content = content[:MAX_CHARS_TEXT]
            return ArtifactPreview(
                artifact_id="",
                content_type="",
                preview_type=preview_type,
                preview_data=redact_text(truncated_content),
                truncated=True,
            )
        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=redact_text(content),
        )

    if isinstance(content, (dict, list)):
        redacted = redact_value(content)
        text = json.dumps(redacted, ensure_ascii=False, default=str)
        if len(text) > MAX_CHARS_TEXT:
            return ArtifactPreview(
                artifact_id="",
                content_type="",
                preview_type=preview_type,
                preview_data=text[:MAX_CHARS_TEXT],
                truncated=True,
            )
        return ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type=preview_type,
            preview_data=text,
        )

    return ArtifactPreview(
        artifact_id="",
        content_type="",
        preview_type=preview_type,
        preview_data=str(content) if content is not None else None,
    )


def build_preview(
    artifact_id: str,
    content_type: str,
    content: Any,
) -> ArtifactPreview:
    preview_type = _infer_preview_type(content_type, content)

    if preview_type == "json":
        result = _preview_json(content)
    elif preview_type == "jsonl":
        result = _preview_jsonl(content)
    elif preview_type == "text":
        result = _preview_text(content)
    else:
        result = ArtifactPreview(
            artifact_id="",
            content_type="",
            preview_type="unsupported",
            metadata_only=True,
        )

    return ArtifactPreview(
        artifact_id=artifact_id,
        content_type=content_type,
        preview_type=result.preview_type,
        preview_data=result.preview_data,
        truncated=result.truncated,
        row_count=result.row_count,
        row_warnings=result.row_warnings,
        error=result.error,
        metadata_only=result.metadata_only,
    )
