from typing import Optional, Dict
from tradegym.engine.core import TObject, PrivateAttr, computed_property, Formula
from .commission import Commission, FreeCommission


__all__ = ["Contract"]



class Contract(TObject):

    _code: str = PrivateAttr()
    _exchange: str = PrivateAttr()
    _commodity: str = PrivateAttr()
    _multiplier: int = PrivateAttr()
    _margin_rate: float = PrivateAttr()
    _tick_size: float = PrivateAttr()
    _commission: Optional[Commission] = PrivateAttr(default_factory=FreeCommission)
    
    @computed_property
    def code(self) -> str:
        return self._code
    
    @computed_property
    def exchange(self) -> str:
        return self._exchange
    
    @computed_property
    def commodity(self) -> str:
        return self._commodity
    
    @computed_property
    def multiplier(self) -> int:
        return self._multiplier
    
    @computed_property
    def margin_rate(self) -> float:
        return self._margin_rate
    
    @computed_property
    def tick_size(self) -> float:
        return self._tick_size
    
    @computed_property
    def commission(self) -> Commission:
        return self._commission
    
    def calculate_notional_value(self, price: float, volume: int) -> float:
        return Formula.contract_notional_value(price, volume, self.multiplier)
    
    def calculate_margin(self, price: float, volume: int) -> float:
        return Formula.contract_margin(price, volume, self.multiplier, self.margin_rate)
