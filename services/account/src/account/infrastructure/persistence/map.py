from sqlalchemy.orm import registry

from account.application.models import RefreshSession, User
from account.infrastructure.persistence.tables import (
    metadata,
    refresh_sessions,
    users,
)


def setup_mappers() -> None:
    mapper_registry = registry(metadata=metadata)

    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(RefreshSession, refresh_sessions)
