from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from fastapi import APIRouter, Path, Query

from account.application.ports.data.account_reader import AccountInfo
from account.application.services.account_service import AccountService
from account.presentation.auth import AuthRequired
from account.presentation.dishka import inject

doctor_router = APIRouter(
    prefix="/Doctors", dependencies=[AuthRequired], tags=["Доктора"]
)


@doctor_router.get("/", status_code=200, summary="Получение списка докторов")
@inject
def all_(
    *,
    name_filter: Annotated[str | None, Query()] = None,
    from_: Annotated[int, Query(alias="from")] = 0,
    count: Annotated[int, Query()] = 10,
    account_service: FromDishka[AccountService],
) -> list[AccountInfo]:
    return account_service.all_doctors(from_, count, name_filter)


@doctor_router.get(
    "/{id}",
    status_code=200,
    summary="Получение информации о докторе по Id",  # noqa: RUF001
    responses={404: {"description": "Doctor not found"}},
)
@inject
def doctor_identified(
    id_: Annotated[UUID, Path(alias="id")],
    account_service: FromDishka[AccountService],
) -> AccountInfo:
    return account_service.doctor_identified(id_)
