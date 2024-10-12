from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class UserRole(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    MANAGER = "MANAGER"


@dataclass(kw_only=True)
class User:
    id: UUID = field(default_factory=uuid4)
    first_name: str
    last_name: str
    username: str
    password_hash: str
    roles: set[UserRole]
    is_active: bool = False


@dataclass(kw_only=True)
class RefreshSession:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID
    refresh_token: str
    expires_in: datetime
    created_at: datetime


@dataclass(kw_only=True)
class TokenPayload:
    user_id: UUID
    roles: set[UserRole]


@dataclass(kw_only=True)
class JwtToken:
    value: str
    payload: TokenPayload
    expires_in: datetime
    created_at: datetime
