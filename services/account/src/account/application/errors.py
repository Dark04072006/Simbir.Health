class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class UserAlreadyDeletedError(Exception):
    pass
