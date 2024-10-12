from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    tz: timezone

    def now(self) -> datetime: ...
