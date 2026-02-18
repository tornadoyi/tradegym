from typing import Optional, ClassVar
from datetime import datetime, timedelta
from tradegym.engine.core import Plugin, Field, writable


__all__ = ['Clock']



class Clock(Plugin):
    Name: ClassVar[str] = 'clock'

    now: datetime = Field(datetime.now())
    step: timedelta = Field(timedelta(milliseconds=500))

    @writable
    def set_now(self, now: datetime) -> None:
        self.now = now

    @writable
    def tick(self) -> datetime:
        self.now += self.step
        return self.now
    
