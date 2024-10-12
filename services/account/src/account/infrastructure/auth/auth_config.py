from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class AuthConfig:
    jwt_secret: str
    access_expiration: timedelta
    refresh_expiration: timedelta
