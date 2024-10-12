from dataclasses import dataclass

from account.application.errors import (
    AuthenticationError,
    InvalidTokenError,
    UserAlreadyExistsError,
)
from account.application.ports.auth.identity_provider import IdentityProvider
from account.application.ports.auth.jwt_token_provider import (
    JwtTokenProvider,
    TokenPayload,
)
from account.application.ports.auth.password_service import PasswordService
from account.application.ports.clock import Clock
from account.application.ports.commitable import Commitable
from account.application.ports.data.refresh_session_gateway import (
    RefreshSessionGateway,
)
from account.application.ports.data.user_gateway import UserGateway
from account.application.ports.factory.refresh_session_factory import (
    RefreshSessionFactory,
)
from account.application.ports.factory.user_factory import UserFactory


@dataclass
class SignUpRequest:
    first_name: str
    last_name: str
    username: str
    password: str


@dataclass
class SignInRequest:
    username: str
    password: str


@dataclass
class CredentialsResponse:
    access_token: str
    refresh_token: str


class AuthenticationService:
    def __init__(
        self,
        clock: Clock,
        commitable: Commitable,
        user_factory: UserFactory,
        user_gateway: UserGateway,
        password_service: PasswordService,
        identity_provider: IdentityProvider,
        jwt_token_provider: JwtTokenProvider,
        refresh_session_factory: RefreshSessionFactory,
        refresh_session_gateway: RefreshSessionGateway,
    ) -> None:
        self._clock = clock
        self._commitable = commitable
        self._user_factory = user_factory
        self._user_gateway = user_gateway
        self._password_service = password_service
        self._identity_provider = identity_provider
        self._jwt_token_provider = jwt_token_provider
        self._refresh_session_factory = refresh_session_factory
        self._refresh_session_gateway = refresh_session_gateway

    def sign_up(self, request: SignUpRequest) -> None:
        if self._user_gateway.exists_named(request.username):
            raise UserAlreadyExistsError("User with this username already exists")

        password_hash = self._password_service.hash(request.password)

        new_user = self._user_factory.standart_user(
            request.first_name,
            request.last_name,
            request.username,
            password_hash,
        )

        self._user_gateway.add(new_user)

        self._commitable.commit()

    def sign_in(self, request: SignInRequest) -> CredentialsResponse:
        user = self._user_gateway.named_with(request.username)

        if user is None:
            raise AuthenticationError("Wrong username or password")

        if not self._password_service.verify(request.password, user.password_hash):
            raise AuthenticationError("Wrong username or password")

        token_payload = TokenPayload(user_id=user.id, roles=user.roles)

        access_token = self._jwt_token_provider.create_access_token(token_payload)
        refresh_token = self._jwt_token_provider.create_refresh_token(token_payload)

        refresh_session = self._refresh_session_factory.from_refresh_token(
            refresh_token.value
        )

        self._refresh_session_gateway.add(refresh_session)

        self._commitable.commit()

        return CredentialsResponse(access_token.value, refresh_token.value)

    def sign_out(self) -> None:
        user_id = self._identity_provider.user_id()

        refresh_session = self._refresh_session_gateway.with_user_id(user_id)

        if refresh_session is None or refresh_session.expires_in < self._clock.now():
            return

        self._refresh_session_gateway.remove(refresh_session)

        self._commitable.commit()

    def validate(self, access_token: str) -> TokenPayload:
        jwt_token = self._jwt_token_provider.validate(access_token)

        return jwt_token.payload

    def refresh(self, refresh_token: str) -> CredentialsResponse:
        refresh_session = self._refresh_session_gateway.with_refresh_token(
            refresh_token
        )

        if refresh_session is None:
            raise InvalidTokenError("Invalid refresh token")

        self._refresh_session_gateway.remove(refresh_session)

        user = self._user_gateway.idenified(refresh_session.user_id)

        if user is None:
            raise InvalidTokenError("Invalid refresh token")

        token_payload = TokenPayload(user_id=user.id, roles=user.roles)

        new_access_token = self._jwt_token_provider.create_access_token(
            token_payload
        )
        new_refresh_token = self._jwt_token_provider.create_refresh_token(
            token_payload
        )

        refresh_session = self._refresh_session_factory.from_refresh_token(
            new_access_token.value
        )

        self._refresh_session_gateway.add(refresh_session)

        self._commitable.commit()

        return CredentialsResponse(new_access_token.value, new_refresh_token.value)
