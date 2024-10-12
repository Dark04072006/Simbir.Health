from uuid import UUID

from fastapi import Request

from account.application.errors import AuthenticationError
from account.application.models import JwtToken, User, UserRole
from account.application.ports.auth.identity_provider import IdentityProvider
from account.application.ports.auth.jwt_token_provider import JwtTokenProvider
from account.application.ports.data.user_gateway import UserGateway
from account.infrastructure.auth.auth_config import AuthConfig


class HttpIdentityProvider(IdentityProvider):
    def __init__(
        self,
        http_request: Request,
        auth_config: AuthConfig,
        user_gateway: UserGateway,
        jwt_token_provider: JwtTokenProvider,
    ) -> None:
        self._http_request = http_request
        self._auth_config = auth_config
        self._user_gateway = user_gateway
        self._jwt_token_provider = jwt_token_provider

    def _introspect(self) -> JwtToken:
        token = self._http_request.headers.get("Authorization")

        if token is None or not token.startswith("Bearer "):
            raise AuthenticationError("Not authenticated")

        token = token.replace("Bearer ", "")

        return self._jwt_token_provider.validate(token)

    def user(self) -> User:
        user = self._user_gateway.idenified(self.user_id())

        if user is None:
            raise AuthenticationError("Not authenticated")

        return user

    def user_id(self) -> UUID:
        introspection = self._introspect()

        return introspection.payload.user_id

    def user_roles(self) -> set[UserRole]:
        introspection = self._introspect()

        return introspection.payload.roles

    def is_authenticated(self) -> bool:
        try:
            self._introspect()

        except AuthenticationError:
            return False

        return True
