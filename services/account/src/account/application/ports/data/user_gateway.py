from typing import Protocol
from uuid import UUID

from account.application.models import User


class UserGateway(Protocol):
    def add(self, user: User) -> None: ...
    def idenified(self, user_id: UUID) -> User | None: ...
    def named_with(self, username: str) -> User | None: ...
    def exists_named(self, username: str) -> bool: ...
    def exists_identified(self, user_id: UUID) -> bool: ...
