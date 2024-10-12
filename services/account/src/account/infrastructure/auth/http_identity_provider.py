from uuid import UUID

from account.application.errors import AuthenticationError
from account.application.models import JwtToken, User, UserRole
from account.application.ports.auth.identity_provider import IdentityProvider
from account.application.ports.auth.jwt_token_provider import JwtTokenProvider
from account.application.ports.data.user_gateway import UserGateway
from account.infrastructure.auth.auth_config import AuthConfig
from account.infrastructure.auth.auth_token_gettable import AuthTokenGettable


class HttpIdentityProvider(IdentityProvider):
    def __init__(
        self,
        auth_config: AuthConfig,
        user_gateway: UserGateway,
        jwt_token_provider: JwtTokenProvider,
        auth_token_gettable: AuthTokenGettable,
    ) -> None:
        self._auth_config = auth_config
        self._user_gateway = user_gateway
        self._jwt_token_provider = jwt_token_provider
        self._auth_token_gettable = auth_token_gettable

    def _introspect(self) -> JwtToken:
        token = self._auth_token_gettable.get_auth_token()

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
