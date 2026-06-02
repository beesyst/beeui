from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from beeui_module.adapters.errors import AdapterError
from beeui_module.adapters.ids import validate_product_id

AdapterStatus = Literal["ok", "partial", "error"]


# Энвелопы для результатов адаптера
@dataclass(frozen=True)
class AdapterWarning:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


# Энвелоп для успешного результата
@dataclass(frozen=True)
class AdapterMetadata:
    product_id: str
    title: str
    version: str
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    supported_pages: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        validate_product_id(self.product_id)
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("AdapterMetadata.title must be a non-empty string")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("AdapterMetadata.version must be a non-empty string")
        for capability in self.capabilities:
            if not isinstance(capability, str) or not capability.strip():
                raise ValueError(
                    "AdapterMetadata.capabilities must contain only non-empty strings"
                )
        for page in self.supported_pages:
            if not isinstance(page, str) or not page.strip():
                raise ValueError(
                    "AdapterMetadata.supported_pages must contain only non-empty strings"
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_id": self.product_id,
            "title": self.title,
            "version": self.version,
            "capabilities": list(self.capabilities),
            "supported_pages": list(self.supported_pages),
        }


# Энвелоп для успешного результата
@dataclass(frozen=True)
class AdapterResult:
    status: Literal["ok", "partial"]
    data: Any
    warnings: tuple[AdapterWarning, ...] = field(default_factory=tuple)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "data": self.data,
            "warnings": [warning.to_dict() for warning in self.warnings],
            "meta": dict(self.meta),
        }


# Энвелоп для результата с ошибкой
@dataclass(frozen=True)
class AdapterErrorResult:
    error: dict[str, str]
    warnings: tuple[AdapterWarning, ...] = field(default_factory=tuple)
    meta: dict[str, Any] = field(default_factory=dict)
    status: Literal["error"] = "error"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "error": dict(self.error),
            "warnings": [warning.to_dict() for warning in self.warnings],
            "meta": dict(self.meta),
        }


# Создание результатов адаптера
def ok_result(
    data: Any,
    *,
    warnings: list[AdapterWarning] | tuple[AdapterWarning, ...] | None = None,
    meta: dict[str, Any] | None = None,
) -> AdapterResult:
    return AdapterResult(
        status="ok",
        data=data,
        warnings=tuple(warnings or ()),
        meta=dict(meta or {}),
    )


# Результат с частичным успехом
def partial_result(
    data: Any,
    *,
    warnings: list[AdapterWarning] | tuple[AdapterWarning, ...] | None = None,
    meta: dict[str, Any] | None = None,
) -> AdapterResult:
    return AdapterResult(
        status="partial",
        data=data,
        warnings=tuple(warnings or ()),
        meta=dict(meta or {}),
    )


# Результат с ошибкой
def error_result(
    code: str,
    message: str,
    *,
    warnings: list[AdapterWarning] | tuple[AdapterWarning, ...] | None = None,
    meta: dict[str, Any] | None = None,
) -> AdapterErrorResult:
    return AdapterErrorResult(
        error={"code": code, "message": message},
        warnings=tuple(warnings or ()),
        meta=dict(meta or {}),
    )


# Создание результата с ошибкой из исключения
def error_result_from_exception(
    exc: Exception,
    *,
    warnings: list[AdapterWarning] | tuple[AdapterWarning, ...] | None = None,
    meta: dict[str, Any] | None = None,
) -> AdapterErrorResult:
    if isinstance(exc, AdapterError):
        return error_result(
            exc.code,
            str(exc),
            warnings=warnings,
            meta=meta,
        )
    return error_result(
        "adapter_error",
        "Adapter error",
        warnings=warnings,
        meta=meta,
    )
