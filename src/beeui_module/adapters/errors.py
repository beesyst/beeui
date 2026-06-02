from __future__ import annotations


class AdapterError(Exception):
    code = "adapter_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)

    def to_error_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": str(self)}


class InvalidIdError(AdapterError):
    code = "invalid_id"


class NotFoundError(AdapterError):
    code = "not_found"


class PermissionDeniedError(AdapterError):
    code = "permission_denied"


class UnavailableError(AdapterError):
    code = "unavailable"


class ValidationError(AdapterError):
    code = "validation_error"