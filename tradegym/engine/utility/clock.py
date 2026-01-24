from typing import Optional, ClassVar
from datetime import datetime, timedelta
from tradegym.engine.core import Plugin, PrivateAttr, computed_property


__all__ = ['Clock']



class Clock(Plugin):
    Name: ClassVar[str] = 'clock'

    _now: datetime = PrivateAttr()

    @computed_property
    def now(self) -> datetime:
        return self._now
    
    def tick(self, delta: timedelta) -> None:
        self._now += delta
    
    
Plugin.register(Clock)