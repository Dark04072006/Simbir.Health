from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from account.application.models import User
from account.application.ports.data.user_gateway import UserGateway


class UserMapper(UserGateway):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(user)

    def idenified(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)

        return self._session.scalar(stmt)

    def named_with(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)

        return self._session.scalar(stmt)

    def exists_named(self, username: str) -> bool:
        stmt = select(exists().where(User.username == username))

        return bool(self._session.scalar(stmt))

    def exists_identified(self, user_id: UUID) -> bool:
        stmt = select(exists().where(User.id == user_id))

        return bool(self._session.scalar(stmt))
