from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from account.application.models import UserRole


@dataclass(frozen=True)
class AccountInfo:
    id: UUID
    first_name: str
    last_name: str
    username: str
    roles: set[UserRole]
    is_active: bool


@dataclass(frozen=True, kw_only=True)
class AccountFilter:
    user_id: UUID | None = None
    role: UserRole | None = None
    only_active: bool = True
    name_filter: str | None = None


@dataclass(frozen=True, kw_only=True)
class ManyAccountFilter(AccountFilter):
    from_: int
    count: int


class AccountReader(Protocol):
    def read(self, filter_: ManyAccountFilter) -> list[AccountInfo]: ...
    def read_one(self, filter_: AccountFilter) -> AccountInfo | None: ...
