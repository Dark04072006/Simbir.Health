from typing import TYPE_CHECKING

from fastapi import FastAPI

from account.application.models import UserRole
from account.application.ports.auth.password_service import PasswordService
from account.application.ports.commitable import Commitable
from account.application.ports.data.user_gateway import UserGateway
from account.application.ports.factory.user_factory import UserFactory

if TYPE_CHECKING:
    from dishka import Container


def initialize_accounts_state_on_startup(app: FastAPI) -> None:
    container: Container = app.state.dishka_container

    with container() as request_container:
        factory: UserFactory = request_container.get(UserFactory)
        commitable: Commitable = request_container.get(Commitable)
        user_gateway: UserGateway = request_container.get(UserGateway)
        password_service: PasswordService = request_container.get(PasswordService)

        admin_user = factory.new_user(
            first_name="Admin",
            last_name="Admin",
            username="admin",
            password_hash=password_service.hash("admin"),
            roles={UserRole.ADMIN},
        )
        manager_user = factory.new_user(
            first_name="Manager",
            last_name="Manager",
            username="manager",
            password_hash=password_service.hash("manager"),
            roles={UserRole.MANAGER},
        )
        doctor_user = factory.new_user(
            first_name="Doctor",
            last_name="Doctor",
            username="doctor",
            password_hash=password_service.hash("doctor"),
            roles={UserRole.DOCTOR},
        )
        standart_user = factory.standart_user(
            first_name="User",
            last_name="User",
            username="user",
            password_hash=password_service.hash("user"),
        )

        if not user_gateway.exists_named(admin_user.username):
            user_gateway.add(admin_user)

        if not user_gateway.exists_named(manager_user.username):
            user_gateway.add(manager_user)

        if not user_gateway.exists_named(doctor_user.username):
            user_gateway.add(doctor_user)

        if not user_gateway.exists_named(standart_user.username):
            user_gateway.add(standart_user)

        commitable.commit()


def setup_event_handlers(app: FastAPI) -> None:
    app.add_event_handler(
        "startup", lambda: initialize_accounts_state_on_startup(app)
    )
