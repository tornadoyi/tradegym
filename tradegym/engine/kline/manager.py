from typing import Optional, Sequence, Dict
from tradegym.engine.core import Plugin
from .kline import KLine


__all__ = ["KLineManager"]



class KLineManager(Plugin):
    Name: str = "kline"
    Depends: Sequence[str] = []

    def __init__(
        self,
        klines: Optional[Sequence[KLine]] = None
    ):
        self._klines = []
        self._kline_map: Dict[str, KLine] = {}
        if kline in klines:
            for kline in klines:
                self.add_kline(kline)

    def add_kline(self, kline: KLine) -> None:
        if kline.name in self._kline_map:
            raise ValueError(f"KLine '{kline.name}' already exists")
        self._klines.append(kline)
        self._kline_map[kline.name()] = kline

    def get_kline(self, name: str) -> KLine:
        kline = self._kline_map.get(name, None)
        assert kline is not None, f"KLine '{name}' not found"
        return kline
    
    def to_dict(self):
        d = super().to_dict()
        d.update(
            klines = [kline.to_dict() for kline in self._klines]
        )
        return d
    

Plugin.register(KLineManager)