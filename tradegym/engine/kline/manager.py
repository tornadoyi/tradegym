from typing import Optional, List, Dict, ClassVar, Union
from datetime import timedelta
from tradegym.engine.core import Plugin, PrivateAttr, computed_property
from .kline import KLine


__all__ = ["KLineManager"]



class KLineManager(Plugin):
    Name: ClassVar[str] = "kline"

    _klines: List[KLine] = PrivateAttr(default_factory=list)
    _code_klines: Dict[str, List[KLine]] = PrivateAttr(default_factory=dict)

    def __init__(self, klines: Optional[List[Union[KLine, Dict]]] = None):
        super().__init__()
        if klines is not None:
            for arg in klines:
                kline = arg if isinstance(arg, KLine) else KLine.from_dict(arg)
                self.add_kline(kline)

    @computed_property
    def klines(self) -> List[KLine]:
        return self._klines
            
    def add_kline(self, kline: KLine) -> None:
        line_lst = self._code_klines.get(kline.code)
        if line_lst is None:
            line_lst = self._code_klines[kline.code] = []
        
        # check
        for line in line_lst:
            if line.timestep == kline.timestep:
                raise ValueError(f"KLine '{kline.code}' with timestamp '{line.timestep}' already exists")
        
        # save
        self._klines.append(kline)
        line_lst.append(kline)
             

    def get_kline(self, code: str, timestep: Optional[timedelta] = None) -> KLine:
        line_lst = self._code_klines.get(code)
        assert line_lst is not None, f"KLine '{code}' not found"
        if timestep is None:
            return line_lst[0]
        else:
            for line in line_lst:
                if line.timestep == timestep:
                    return line
            raise ValueError(f"KLine '{code}' with timestamp '{timestep}' not found")
    

Plugin.register(KLineManager)