from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Any


# Модуль: модели данных для аутентификации, включая роли пользователей и структуру сессии
class UserRole(str, enum.Enum):
    viewer = "viewer"
    operator = "operator"
    admin = "admin"


_ROLE_HIERARCHY: dict[UserRole, int] = {
    UserRole.viewer: 0,
    UserRole.operator: 1,
    UserRole.admin: 2,
}


# Возвращение True если роль пользователя соответствует или выше требуемой минимальной роли
def role_meets_minimum(role: UserRole, minimum: UserRole) -> bool:
    return _ROLE_HIERARCHY.get(role, -1) >= _ROLE_HIERARCHY.get(minimum, 999)


# Класс: данные сессии пользователя, включая ID, роль и CSRF токен
@dataclass(frozen=True)
class SessionData:
    user_id: str
    role: UserRole
    csrf_token: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "csrf_token": self.csrf_token,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionData:
        return cls(
            user_id=str(data["user_id"]),
            role=UserRole(str(data["role"])),
            csrf_token=str(data["csrf_token"]),
            created_at=float(data.get("created_at", 0)),
        )
