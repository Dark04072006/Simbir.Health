from account.application.models import User, UserRole
from account.application.ports.factory.user_factory import UserFactory


class UserFactoryImpl(UserFactory):
    def standart_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        password_hash: str,
    ) -> User:
        return User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password_hash=password_hash,
            roles={UserRole.USER},
            is_active=True,
        )

    def new_user(
        self,
        first_name: str,
        last_name: str,
        username: str,
        password_hash: str,
        roles: set[UserRole],
    ) -> User:
        return User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password_hash=password_hash,
            roles=roles,
            is_active=True,
        )
