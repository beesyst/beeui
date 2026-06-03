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


# Чек: нужно ли редактировать значение по ключу
def _should_redact(key: str) -> bool:
    lowered = key.lower().replace("-", "_")
    return lowered in _REDACT_KEYS or any(
        pattern in lowered for pattern in _REDACT_KEYS
    )


# Рекурсивная редакция чувствительных данных в структуре JSON
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


# Редакция чувствительных данных в текстовом формате (консервативный подход)
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
