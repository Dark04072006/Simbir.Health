from typing import Protocol

from account.application.models import User, UserRole


class UserFactory(Protocol):
    def standart_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        password_hash: str,
    ) -> User: ...
    def new_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        password_hash: str,
        roles: set[UserRole],
    ) -> User: ...
