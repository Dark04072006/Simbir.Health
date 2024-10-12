from dataclasses import dataclass
from uuid import UUID

from account.application.errors import (
    AuthenticationError,
    AuthorizationError,
    UserAlreadyDeletedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from account.application.models import UserRole
from account.application.ports.auth.identity_provider import IdentityProvider
from account.application.ports.auth.password_service import PasswordService
from account.application.ports.commitable import Commitable
from account.application.ports.data.account_reader import (
    AccountFilter,
    AccountInfo,
    AccountReader,
    ManyAccountFilter,
)
from account.application.ports.data.user_gateway import UserGateway
from account.application.ports.factory.user_factory import UserFactory


@dataclass
class UpdateMeRequest:
    first_name: str
    last_name: str
    username: str


@dataclass
class AccountRequest:
    first_name: str
    last_name: str
    username: str
    password: str
    roles: set[UserRole]


class AccountService:
    def __init__(
        self,
        commitable: Commitable,
        user_gateway: UserGateway,
        user_factory: UserFactory,
        account_reader: AccountReader,
        password_service: PasswordService,
        identity_provider: IdentityProvider,
    ) -> None:
        self._commitable = commitable
        self._user_gateway = user_gateway
        self._user_factory = user_factory
        self._account_reader = account_reader
        self._password_service = password_service
        self._identity_provider = identity_provider

    def get_me(self) -> AccountInfo:
        user_id = self._identity_provider.user_id()

        account = self._account_reader.read_one(AccountFilter(user_id=user_id))

        if account is None:
            raise AuthenticationError("Not authenticated")

        return account

    def update_me(self, request: UpdateMeRequest) -> None:
        user = self._identity_provider.user()

        if self._user_gateway.exists_named(request.username):
            raise UserAlreadyExistsError("User with this username already exists")

        user.first_name = request.first_name
        user.last_name = request.last_name
        user.username = request.username

        self._commitable.commit()

    def all_accounts(self, from_: int, count: int) -> list[AccountInfo]:
        roles = self._identity_provider.user_roles()

        if not any(role == UserRole.ADMIN for role in roles):
            raise AuthorizationError("Access denied")

        filter_ = ManyAccountFilter(
            from_=from_,
            count=count,
            only_active=False,
        )
        return self._account_reader.read(filter_)

    def create_account(self, request: AccountRequest) -> None:
        roles = self._identity_provider.user_roles()

        if not any(role == UserRole.ADMIN for role in roles):
            raise AuthorizationError("Access denied")

        if self._user_gateway.exists_named(request.username):
            raise UserAlreadyExistsError("User with this username already exists")

        password_hash = self._password_service.hash(request.password)

        new_user = self._user_factory.new_user(
            request.first_name,
            request.last_name,
            request.username,
            password_hash,
            request.roles,
        )

        self._user_gateway.add(new_user)

        self._commitable.commit()

    def update_account(self, id_: UUID, request: AccountRequest) -> None:
        roles = self._identity_provider.user_roles()

        if not any(role == UserRole.ADMIN for role in roles):
            raise AuthorizationError("Access denied")

        user = self._user_gateway.idenified(id_)

        if user is None:
            raise UserNotFoundError("User with this id not found")

        if self._user_gateway.exists_named(request.username):
            raise UserAlreadyExistsError("User with this username already exists")

        user.first_name = request.first_name
        user.last_name = request.last_name
        user.username = request.username
        user.roles = request.roles

        self._commitable.commit()

    def delete_account(self, id_: UUID) -> None:
        roles = self._identity_provider.user_roles()

        if not any(role == UserRole.ADMIN for role in roles):
            raise AuthorizationError("Access denied")

        user = self._user_gateway.idenified(id_)

        if user is None:
            raise UserNotFoundError("User with this id not found")

        if not user.is_active:
            raise UserAlreadyDeletedError("User already deleted")

        user.is_active = True

        self._commitable.commit()

    def all_doctors(
        self,
        from_: int,
        count: int,
        name_filter: str | None = None,
    ) -> list[AccountInfo]:
        if not self._identity_provider.is_authenticated():
            raise AuthenticationError("Not authenticated")

        filter_ = ManyAccountFilter(
            from_=from_,
            count=count,
            only_active=True,
            name_filter=name_filter,
        )
        return self._account_reader.read(filter_)

    def doctor_identified(self, id_: UUID) -> AccountInfo:
        if not self._identity_provider.is_authenticated():
            raise AuthenticationError("Not authenticated")

        filter_ = AccountFilter(user_id=id_, only_active=True, role=UserRole.DOCTOR)

        account = self._account_reader.read_one(filter_)

        if account is None:
            raise UserNotFoundError("User with this id not found")

        return account
