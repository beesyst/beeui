from __future__ import annotations

from copy import deepcopy
from typing import Any

_REDACT_KEYS = frozenset(
    {
        "secret",
        "token",
        "password",
        "api_key",
        "api_secret",
        "authorization",
        "cookie",
        "session",
        "credential",
        "passphrase",
        "private_key",
        "access_key",
        "access_token",
        "refresh_token",
        "auth_token",
    }
)
_REDACTED_PLACEHOLDER = "*** REDACTED ***"


def _should_redact(key: str) -> bool:
    lowered = key.lower().replace("-", "_")
    return lowered in _REDACT_KEYS or any(
        pattern in lowered for pattern in _REDACT_KEYS
    )


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for k, v in value.items():
            if _should_redact(str(k)):
                result[k] = _REDACTED_PLACEHOLDER
            else:
                result[k] = redact_value(v)
        return result

    if isinstance(value, list):
        return [redact_value(item) for item in value]

    return deepcopy(value)


def redact_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    result_lines: list[str] = []
    for line in lines:
        stripped = line.strip().lower()
        if any(pattern in stripped for pattern in _REDACT_KEYS):
            result_lines.append(f"{_REDACTED_PLACEHOLDER}\n")
        else:
            result_lines.append(line)
    return "".join(result_lines)


def redact_adapter_message(message: Any) -> str:
    return redact_text(str(message))


def redact_adapter_error(error: dict[str, Any]) -> dict[str, Any]:
    redacted = redact_value(error)
    redacted["message"] = redact_adapter_message(error.get("message", "Adapter error"))
    return redacted


def redact_adapter_warnings(warnings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    redacted = redact_value(warnings)
    for original, warning in zip(warnings, redacted, strict=True):
        if isinstance(warning, dict) and "message" in original:
            warning["message"] = redact_adapter_message(original["message"])
    return redacted
