from collections.abc import Iterable

from dishka import (
    Container,
    Provider,
    Scope,
    alias,
    from_context,
    make_container,
    provide,
)
from fastapi import Request
from passlib.context import CryptContext
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from account.application.ports.auth.identity_provider import IdentityProvider
from account.application.ports.auth.jwt_token_provider import JwtTokenProvider
from account.application.ports.auth.password_service import PasswordService
from account.application.ports.clock import Clock
from account.application.ports.commitable import Commitable
from account.application.ports.data.account_reader import AccountReader
from account.application.ports.data.refresh_session_gateway import (
    RefreshSessionGateway,
)
from account.application.ports.data.user_gateway import UserGateway
from account.application.ports.factory.refresh_session_factory import (
    RefreshSessionFactory,
)
from account.application.ports.factory.user_factory import UserFactory
from account.application.services.account_service import AccountService
from account.application.services.authentication_service import AuthenticationService
from account.infrastructure.auth.auth_config import AuthConfig
from account.infrastructure.auth.http_identity_provider import (
    HttpIdentityProvider,
)
from account.infrastructure.auth.jose_jwt_token_provider import (
    JoseJwtTokenProvider,
)
from account.infrastructure.auth.passlib_password_service import (
    PasslibPasswordService,
)
from account.infrastructure.factory.refresh_session_factory import (
    RefreshSessionFactoryImpl,
)
from account.infrastructure.factory.user_factory import UserFactoryImpl
from account.infrastructure.persistence.account_reader import (
    SqlalchemyAccountReader,
)
from account.infrastructure.persistence.data_mappers.refresh_session_mapper import (
    RefreshSessionMapper,
)
from account.infrastructure.persistence.data_mappers.user_mapper import (
    UserMapper,
)
from account.infrastructure.utc_clock import UTCClock

type ConnectionString = str


class PersistenceProvider(Provider):
    connection_string = from_context(ConnectionString, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def provide_engine(
        self, connection_string: ConnectionString
    ) -> Iterable[Engine]:
        engine = create_engine(connection_string)

        yield engine

        engine.dispose()

    @provide(scope=Scope.APP)
    def provide_sessionmaker(self, engine: Engine) -> sessionmaker[Session]:
        return sessionmaker(bind=engine)

    @provide(scope=Scope.REQUEST)
    def provide_session(
        self, sessionmaker: sessionmaker[Session]
    ) -> Iterable[Session]:
        with sessionmaker() as session:
            yield session

    commitable = alias(source=Session, provides=Commitable)

    account_reader = provide(
        SqlalchemyAccountReader,
        scope=Scope.REQUEST,
        provides=AccountReader,
    )
    user_gateway = provide(
        UserMapper,
        scope=Scope.REQUEST,
        provides=UserGateway,
    )
    refresh_session_gateway = provide(
        RefreshSessionMapper,
        scope=Scope.REQUEST,
        provides=RefreshSessionGateway,
    )


class FactoryProvider(Provider):
    scope = Scope.APP

    user_factory = provide(UserFactoryImpl, provides=UserFactory)
    refresh_session_factory = provide(
        RefreshSessionFactoryImpl, provides=RefreshSessionFactory
    )


class AuthProvider(Provider):
    request = from_context(Request, scope=Scope.REQUEST)
    auth_config = from_context(AuthConfig, scope=Scope.APP)

    identity_provider = provide(
        HttpIdentityProvider,
        scope=Scope.REQUEST,
        provides=IdentityProvider,
    )
    jwt_token_provider = provide(
        JoseJwtTokenProvider,
        scope=Scope.APP,
        provides=JwtTokenProvider,
    )
    password_service = provide(
        PasslibPasswordService,
        scope=Scope.APP,
        provides=PasswordService,
    )

    @provide(scope=Scope.APP)
    def provide_crypt_context(self) -> CryptContext:
        return CryptContext(schemes=["bcrypt"], deprecated="auto")


class ClockProvider(Provider):
    clock = provide(UTCClock, scope=Scope.APP, provides=Clock)


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    account_service = provide(AccountService)
    authentication_service = provide(AuthenticationService)


PROVIDERS = (
    AuthProvider(),
    ClockProvider(),
    FactoryProvider(),
    ServicesProvider(),
    PersistenceProvider(),
)


def setup_container(context: dict) -> Container:
    return make_container(*PROVIDERS, context=context)
