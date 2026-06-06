from __future__ import annotations

import re

from beeui_module.adapters.errors import InvalidIdError

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


# Валидация идентификаторов для продуктов, запусков, артефактов и действий
def validate_product_id(product_id: str) -> str:
    return _validate_safe_id(product_id, field_name="product_id")


# Валидация идентификаторов для запусков, артефактов и действий
def validate_run_id(run_id: str) -> str:
    return _validate_safe_id(run_id, field_name="run_id")


# Валидация идентификаторов для площадок, запусков, артефактов и действий
def validate_venue_id(venue_id: str) -> str:
    return _validate_safe_id(venue_id, field_name="venue_id")


# Валидация идентификаторов для артефактов и действий
def validate_artifact_id(artifact_id: str) -> str:
    return _validate_safe_id(artifact_id, field_name="artifact_id")


# Валидация идентификаторов для действий
def validate_action_id(action_id: str) -> str:
    return _validate_safe_id(action_id, field_name="action_id")


# Чек безопасных идентификаторов
def _validate_safe_id(value: str, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise InvalidIdError(f"{field_name} must be a string")
    if not value:
        raise InvalidIdError(f"{field_name} must be a non-empty string")
    if not value.strip():
        raise InvalidIdError(f"{field_name} must not be whitespace-only")
    if value != value.strip():
        raise InvalidIdError(
            f"{field_name} must not have leading or trailing whitespace"
        )

    lowered = value.lower()
    forbidden_parts = (
        "..",
        "/",
        "\\",
        "://",
        "?",
        "#",
        "&",
        "=",
        ";",
        "|",
        "`",
        "$",
        "*",
    )
    if any(part in lowered for part in forbidden_parts):
        raise InvalidIdError(f"{field_name} contains unsafe characters")

    if value.startswith((".", "~", "-")):
        raise InvalidIdError(f"{field_name} must not start with '.', '~' or '-'")

    if not _SAFE_ID_RE.fullmatch(value):
        raise InvalidIdError(
            f"{field_name} must match safe id pattern [A-Za-z0-9][A-Za-z0-9._-]{{0,63}}"
        )

    return value
