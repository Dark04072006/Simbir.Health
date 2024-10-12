from account.application.models import RefreshSession
from account.application.ports.auth.jwt_token_provider import JwtTokenProvider
from account.application.ports.factory.refresh_session_factory import (
    RefreshSessionFactory,
)


class RefreshSessionFactoryImpl(RefreshSessionFactory):
    def __init__(self, jwt_token_provider: JwtTokenProvider) -> None:
        self._jwt_token_provider = jwt_token_provider

    def from_refresh_token(self, refresh_token: str) -> RefreshSession:
        jwt_token = self._jwt_token_provider.validate(refresh_token)

        return RefreshSession(
            refresh_token=refresh_token,
            expires_in=jwt_token.expires_in,
            created_at=jwt_token.created_at,
            user_id=jwt_token.payload.user_id,
        )
