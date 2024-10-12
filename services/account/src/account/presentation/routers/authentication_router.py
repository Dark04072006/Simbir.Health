from typing import Annotated

from dishka import FromDishka
from fastapi import APIRouter, Body, Query

from account.application.models import TokenPayload
from account.application.services.authentication_service import (
    AuthenticationService,
    CredentialsResponse,
    SignInRequest,
    SignUpRequest,
)
from account.presentation.auth import AuthRequired
from account.presentation.dishka import inject
from account.presentation.models import Message

authentication_router = APIRouter(
    prefix="/Authentication", tags=["Аутентификация и авторизация"]
)


@authentication_router.post(
    "/SignUp",
    status_code=201,
    summary="Регистрация нового аккаунта",
    responses={
        201: {"model": Message, "description": "Account created"},
        409: {
            "model": Message,
            "description": "Account with this username already exists",
        },
    },
)
@inject
def sign_up(
    request: SignUpRequest,
    authentication_service: FromDishka[AuthenticationService],
) -> Message:
    authentication_service.sign_up(request)

    return Message("Account created")


@authentication_router.post(
    "/SignIn",
    status_code=200,
    summary="Получение новой пары jwt пользователя",
    responses={
        200: {"model": CredentialsResponse},
        401: {"model": Message, "description": "Invalid username or password"},
    },
)
@inject
def sign_in(
    request: SignInRequest,
    authentication_service: FromDishka[AuthenticationService],
) -> CredentialsResponse:
    return authentication_service.sign_in(request)


@authentication_router.put(
    "/SignOut",
    status_code=204,
    dependencies=[AuthRequired],
    summary="Выход из аккаунта",
)
@inject
def sign_out(
    authentication_service: FromDishka[AuthenticationService],
) -> None:
    authentication_service.sign_out()


@authentication_router.get(
    "/Validate",
    status_code=200,
    summary="Интроспекция токена",
    responses={
        200: {"model": TokenPayload},
        401: {"model": Message, "description": "Invalid token"},
    },
)
@inject
def validate(
    access_token: Annotated[str, Query(required=True, alias="accessToken")],
    authentication_service: FromDishka[AuthenticationService],
) -> TokenPayload:
    return authentication_service.validate(access_token)


@authentication_router.post(
    "/Refresh",
    status_code=200,
    summary="Обновление пары токенов",
    responses={
        200: {"model": CredentialsResponse},
        401: {"model": Message, "description": "Invalid refresh token"},
    },
)
@inject
def refresh(
    refresh_token: Annotated[str, Body(required=True, alias="refreshToken")],
    authentication_service: FromDishka[AuthenticationService],
) -> CredentialsResponse:
    return authentication_service.refresh(refresh_token)
