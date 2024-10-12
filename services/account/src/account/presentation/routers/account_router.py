from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from fastapi import APIRouter, Path, Query

from account.application.ports.data.account_reader import AccountInfo
from account.application.services.account_service import (
    AccountRequest,
    AccountService,
    UpdateMeRequest,
)
from account.presentation.auth import AuthRequired
from account.presentation.dishka import inject
from account.presentation.models import Message

account_router = APIRouter(
    prefix="/Accounts", dependencies=[AuthRequired], tags=["Аккаунты"]
)


@account_router.get(
    "/Me",
    status_code=200,
    summary="Получение данных о текущем аккаунте",  # noqa: RUF001
)
@inject
def me(account_service: FromDishka[AccountService]) -> AccountInfo:
    return account_service.get_me()


@account_router.put(
    "/Update",
    status_code=204,
    summary="Обновление своего аккаунта",
    responses={409: {"model": Message, "description": "Username already used"}},
)
@inject
def update_me(
    request: UpdateMeRequest,
    account_service: FromDishka[AccountService],
) -> None:
    account_service.update_me(request)


@account_router.get("/", status_code=200, summary="Получение списка аккаунтов")
@inject
def all_(
    *,
    from_: Annotated[int, Query(alias="from")] = 0,
    count: Annotated[int, Query()] = 10,
    account_service: FromDishka[AccountService],
) -> list[AccountInfo]:
    return account_service.all_accounts(from_, count)


@account_router.get(
    "/{id}",
    status_code=201,
    summary="Создание администратором нового аккаунта",
    responses={
        201: {"model": Message, "description": "Account created"},
        409: {"model": Message, "description": "User already exists"},
    },
)
@inject
def create(
    request: AccountRequest,
    account_service: FromDishka[AccountService],
) -> Message:
    account_service.create_account(request)

    return Message("Account created")


@account_router.put(
    "/{id}",
    status_code=204,
    summary="Изменение администратором аккаунта по id",
    responses={404: {"model": Message, "description": "Account not found"}},
)
@inject
def update(
    id_: Annotated[UUID, Path(alias="id")],
    request: AccountRequest,
    account_service: FromDishka[AccountService],
) -> None:
    account_service.update_account(id_, request)


@account_router.delete(
    "/{id}",
    status_code=204,
    summary="Мягкое удаление аккаунта по id",
    responses={
        404: {"model": Message, "description": "Account not found"},
        410: {"model": Message, "description": "Account already deleted"},
    },
)
@inject
def delete(
    id_: Annotated[UUID, Path(alias="id")],
    account_service: FromDishka[AccountService],
) -> None:
    account_service.delete_account(id_)
