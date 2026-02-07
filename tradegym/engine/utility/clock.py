from typing import Optional, ClassVar
from datetime import datetime, timedelta
from tradegym.engine.core import Plugin, PrivateAttr, computed_property


__all__ = ['Clock']



class Clock(Plugin):
    Name: ClassVar[str] = 'clock'

    _now: datetime = PrivateAttr(datetime.now())
    _step: timedelta = PrivateAttr(timedelta(milliseconds=500))

    @computed_property
    def now(self) -> datetime:
        return self._now
    
    @now.setter
    def now(self, value: datetime) -> None:
        self._now = value
    
    @computed_property
    def step(self) -> timedelta:
        return self._step
    
    def tick(self) -> datetime:
        self._now += self._step
        return self._now
    
    
Plugin.register(Clock)