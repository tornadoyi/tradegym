from typing import Optional, List, Dict, ClassVar
from tradegym.engine.core import Plugin, PrivateAttr, computed_property
from .kline import KLine


__all__ = ["KLineManager"]



class KLineManager(Plugin):
    Name: ClassVar[str] = "kline"

    _klines: List[KLine] = PrivateAttr(default_factory=list)
    _kline_map: Dict[str, KLine] = PrivateAttr(default_factory=dict)

    def __init__(self, klines: Optional[List[KLine]] = None):
        super().__init__()
        if klines is not None:
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
    

Plugin.register(KLineManager)