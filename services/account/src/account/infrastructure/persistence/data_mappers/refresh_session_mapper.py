from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from account.application.models import RefreshSession
from account.application.ports.data.refresh_session_gateway import (
    RefreshSessionGateway,
)


class RefreshSessionMapper(RefreshSessionGateway):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, refresh_session: RefreshSession) -> None:
        self._session.add(refresh_session)

    def remove(self, refresh_session: RefreshSession) -> None:
        self._session.delete(refresh_session)

    def with_user_id(self, user_id: UUID) -> RefreshSession | None:
        stmt = select(RefreshSession).where(RefreshSession.user_id == user_id)

        return self._session.scalar(stmt)

    def with_refresh_token(self, refresh_token: str) -> RefreshSession | None:
        stmt = select(RefreshSession).where(
            RefreshSession.refresh_token == refresh_token
        )

        return self._session.scalar(stmt)

    def exists_with_refresh(self, refresh_token: str) -> bool:
        stmt = select(exists().where(RefreshSession.refresh_token == refresh_token))

        return bool(self._session.scalar(stmt))
