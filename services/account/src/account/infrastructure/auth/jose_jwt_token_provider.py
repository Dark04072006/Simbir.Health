from datetime import datetime
from uuid import UUID

from jose import JWTError, jwt

from account.application.errors import InvalidTokenError
from account.application.models import JwtToken, TokenPayload, UserRole
from account.application.ports.auth.jwt_token_provider import JwtTokenProvider
from account.application.ports.clock import Clock
from account.infrastructure.auth.auth_config import AuthConfig


class JoseJwtTokenProvider(JwtTokenProvider):
    def __init__(self, clock: Clock, auth_config: AuthConfig) -> None:
        self._clock = clock
        self._auth_config = auth_config

    def validate(self, token: str) -> JwtToken:
        try:
            credentials = jwt.decode(
                token, key=self._auth_config.jwt_secret, algorithms=["HS256"]
            )

        except JWTError as e:
            raise InvalidTokenError("Invalid token") from e

        expires_in = datetime.fromtimestamp(credentials["exp"], self._clock.tz)
        created_at = datetime.fromtimestamp(credentials["iat"], self._clock.tz)

        if expires_in < self._clock.now():
            raise InvalidTokenError("Token expired")

        payload = TokenPayload(
            user_id=UUID(credentials["user_id"]),
            roles={UserRole(user_role) for user_role in credentials["roles"]},
        )

        return JwtToken(
            value=token,
            payload=payload,
            expires_in=expires_in,
            created_at=created_at,
        )

    def create_access_token(self, payload: TokenPayload) -> JwtToken:
        now = self._clock.now()
        to_encode = {
            "user_id": str(payload.user_id),
            "roles": [role.value for role in payload.roles],
            "iat": int(now.timestamp()),
            "exp": int((now + self._auth_config.access_expiration).timestamp()),
        }

        token = jwt.encode(
            to_encode, self._auth_config.jwt_secret, algorithm="HS256"
        )

        return JwtToken(
            value=token,
            payload=payload,
            expires_in=now + self._auth_config.access_expiration,
            created_at=now,
        )

    def create_refresh_token(self, payload: TokenPayload) -> JwtToken:
        now = self._clock.now()
        to_encode = {
            "user_id": str(payload.user_id),
            "roles": [role.value for role in payload.roles],
            "iat": int(now.timestamp()),
            "exp": int((now + self._auth_config.refresh_expiration).timestamp()),
        }

        token = jwt.encode(
            to_encode, self._auth_config.jwt_secret, algorithm="HS256"
        )

        return JwtToken(
            value=token,
            payload=payload,
            expires_in=now + self._auth_config.refresh_expiration,
            created_at=now,
        )
