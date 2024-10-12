from sqlalchemy import RowMapping, func, select
from sqlalchemy.orm import Session

from account.application.ports.data.account_reader import (
    AccountFilter,
    AccountInfo,
    AccountReader,
    ManyAccountFilter,
)
from account.infrastructure.persistence.tables import users


class SqlalchemyAccountReader(AccountReader):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _load(self, row: RowMapping) -> AccountInfo:
        return AccountInfo(
            id=row["id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            roles=set(row["roles"]),
            is_active=row["is_active"],
        )

    def read(self, filter_: ManyAccountFilter) -> list[AccountInfo]:
        stmt = select(users).offset(filter_.from_).limit(filter_.count)

        if filter_.user_id:
            stmt = stmt.where(users.c.id == filter_.user_id)

        if filter_.role:
            stmt = stmt.where(users.c.roles.contains(filter_.role.value))

        if filter_.name_filter:
            stmt = stmt.where(
                func.concat(
                    users.c.first_name,
                    " ",
                    users.c.last_name,
                ).ilike(
                    filter_.name_filter,
                )
            )

        if filter_.only_active:
            stmt = stmt.where(users.c.is_active is True)

        return [self._load(row) for row in self._session.execute(stmt).mappings()]

    def read_one(self, filter_: AccountFilter) -> AccountInfo | None:
        stmt = select(users)

        if filter_.user_id:
            stmt = stmt.where(users.c.id == filter_.user_id)

        if filter_.role:
            stmt = stmt.where(users.c.roles.contains(filter_.role.value))

        if filter_.name_filter:
            stmt = stmt.where(
                func.concat(users.c.first_name, " ", users.c.last_name).ilike(
                    filter_.name_filter
                )
            )

        if filter_.only_active:
            stmt = stmt.where(users.c.is_active.is_(True))

        row = self._session.execute(stmt).mappings().one_or_none()

        if row is None:
            return None

        return self._load(row)
