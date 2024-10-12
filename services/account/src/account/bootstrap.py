from datetime import timedelta
from os import environ

from fastapi import FastAPI

from account.infrastructure.auth.auth_config import AuthConfig
from account.infrastructure.persistence.map import setup_mappers
from account.infrastructure.providers import ConnectionString, setup_container
from account.presentation.dishka import setup_dishka
from account.presentation.event_handlers import setup_event_handlers
from account.presentation.exception_handlers import setup_exception_handlers
from account.presentation.models import Message
from account.presentation.routers import (
    account_router,
    authentication_router,
    doctor_router,
)


def get_auth_config() -> AuthConfig:
    return AuthConfig(
        jwt_secret=environ["JWT_SECRET"],
        access_expiration=timedelta(seconds=int(environ["ACCESS_TOKEN_EXPIRATION"])),
        refresh_expiration=timedelta(
            seconds=int(environ["REFRESH_TOKEN_EXPIRATION"])
        ),
    )


def get_db_connection_string() -> ConnectionString:
    return environ["DB_CONNECTION_STRING"]


def bootstrap() -> FastAPI:
    app = FastAPI(
        root_path="/api",
        docs_url="/ui-swagger",
        redoc_url=None,
        responses={
            403: {"model": Message, "description": "Access denied"},
            401: {"model": Message, "description": "User is not authenticated"},
        },
        title="Микросервис аккаунтов платформы Simbir.Health",
    )

    app.include_router(account_router)
    app.include_router(authentication_router)
    app.include_router(doctor_router)

    auth_config = get_auth_config()
    db_connection_string = get_db_connection_string()

    context = {
        AuthConfig: auth_config,
        ConnectionString: db_connection_string,
    }
    container = setup_container(context)

    setup_mappers()
    setup_event_handlers(app)
    setup_dishka(app, container)
    setup_exception_handlers(app)

    return app
