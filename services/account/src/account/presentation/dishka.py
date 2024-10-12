from collections.abc import Awaitable, Callable
from inspect import Parameter
from typing import ParamSpec, get_type_hints

from dishka import Container
from dishka.integrations.base import wrap_injection
from fastapi import FastAPI, Request, Response

P = ParamSpec("P")


def inject[T](func: Callable[P, T]) -> Callable[P, T]:
    hints = get_type_hints(func)
    request_hint = next(
        (name for name, hint in hints.items() if hint is Request),
        None,
    )
    if request_hint is None:
        additional_params = [
            Parameter(
                name="___dishka_request",
                annotation=Request,
                kind=Parameter.KEYWORD_ONLY,
            ),
        ]
    else:
        additional_params = []
    param_name = request_hint or "___dishka_request"
    return wrap_injection(
        func=func,
        is_async=False,
        additional_params=additional_params,
        container_getter=lambda _, p: p[param_name].state.dishka_container,
    )


async def dishka_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    container: Container = request.app.state.dishka_container

    with container({Request: request}) as request_container:
        request.state.dishka_container = request_container

        return await call_next(request)


def set_container(app: FastAPI, container: Container) -> None:
    app.state.dishka_container = container


def unset_container(app: FastAPI) -> None:
    app.state.dishka_container.close()

    del app.state.dishka_container


def setup_dishka(app: FastAPI, container: Container) -> None:
    set_container(app, container)

    app.middleware("http")(dishka_middleware)
    app.add_event_handler("shutdown", lambda: unset_container(app))
