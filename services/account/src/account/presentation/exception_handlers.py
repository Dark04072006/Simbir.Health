from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from account.application.errors import (
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    UserAlreadyDeletedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)


async def user_not_found_handler(_: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": str(exc)})


async def user_already_exists_handler(
    _: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"message": str(exc)})


async def authentication_error_handler(
    _: Request, exc: AuthenticationError
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"message": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def authorization_error_handler(
    _: Request, exc: AuthorizationError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"message": str(exc)})


async def invalid_token_error_handler(
    _: Request, exc: InvalidTokenError
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"message": str(exc)},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def user_already_deleted_handler(
    _: Request, exc: UserAlreadyDeletedError
) -> JSONResponse:
    return JSONResponse(status_code=410, content={"message": str(exc)})


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(AuthenticationError, authentication_error_handler)
    app.add_exception_handler(AuthorizationError, authorization_error_handler)
    app.add_exception_handler(InvalidTokenError, invalid_token_error_handler)
    app.add_exception_handler(UserAlreadyDeletedError, user_already_deleted_handler)
