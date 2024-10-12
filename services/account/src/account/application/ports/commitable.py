from typing import Protocol


class Commitable(Protocol):
    def commit(self) -> None: ...
