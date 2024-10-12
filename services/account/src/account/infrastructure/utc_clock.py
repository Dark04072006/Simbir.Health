from datetime import UTC, datetime

from account.application.ports.clock import Clock


class UTCClock(Clock):
    def __init__(self) -> None:
        self.tz = UTC

    def now(self) -> datetime:
        return datetime.now(self.tz)
