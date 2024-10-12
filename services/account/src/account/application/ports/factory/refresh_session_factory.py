from typing import Protocol

from account.application.models import RefreshSession


class RefreshSessionFactory(Protocol):
    def from_refresh_token(self, refresh_token: str) -> RefreshSession: ...
