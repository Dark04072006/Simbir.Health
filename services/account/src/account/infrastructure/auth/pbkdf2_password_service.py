from passlib.context import CryptContext

from account.application.ports.auth.password_service import PasswordService


class Pbkdf2PasswordService(PasswordService):
    def __init__(self, crypt_context: CryptContext) -> None:
        self._crypt_context = crypt_context

    def hash(self, plain_password: str) -> str:
        return self._crypt_context.hash(plain_password)

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return self._crypt_context.verify(plain_password, password_hash)
