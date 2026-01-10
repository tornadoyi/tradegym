from typing import Optional, Callable, Dict, Any, Sequence
from datetime import datetime, timedelta
from tradegym.engine.core import Plugin


__all__ = ['Clock']



class Clock(Plugin):
    Name: str = 'clock'
    Depends: Sequence[str] = ['home']

    def __init__(self, now: Optional[datetime] = None):
        self._now = now
        self._tick_callbacks = set()

    @property
    def now(self) -> datetime:
        return self._now
    
    def tick(self, delta: timedelta) -> None:
        self._now += delta
        for cb in self._tick_callbacks:
            cb(delta)

    def add_tick_callback(self, callback: Callable[[timedelta], None]) -> None:
        self._tick_callbacks.add(callback)

    def del_tick_callback(self, callback: Callable[[timedelta], None]) -> None:
        self._tick_callbacks.remove(callback)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Clock":
        return cls(datetime.fromisoformat(data['now']))
    
    def to_dict(self) -> Dict[str, Any]:
        d = super().to_dict()
        d.update(now=self.now.isoformat())
        return d
    
    
Plugin.register(Clock)