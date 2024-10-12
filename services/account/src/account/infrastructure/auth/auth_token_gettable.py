from typing import Protocol


class AuthTokenGettable(Protocol):
    def get_auth_token(self) -> str: ...
