from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    MetaData,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import ARRAY

from account.application.models import UserRole

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("first_name", String),
    Column("last_name", String),
    Column("username", String),
    Column("password_hash", String),
    Column("is_active", Boolean),
    Column("roles", ARRAY(Enum(UserRole))),
)


refresh_sessions = Table(
    "refresh_sessions",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("user_id", ForeignKey("users.id")),
    Column("refresh_token", String),
    Column("expires_in", DateTime),
    Column("created_at", DateTime),
)
