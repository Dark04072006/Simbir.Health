from account.presentation.routers.account_router import account_router
from account.presentation.routers.authentication_router import (
    authentication_router,
)
from account.presentation.routers.doctor_router import doctor_router

__all__ = (
    "account_router",
    "authentication_router",
    "doctor_router",
)
