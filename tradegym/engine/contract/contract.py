from typing import Optional, Dict, TypeVar
from tradegym.engine.core import TObject, PrivateAttr, computed_property, Formula
from .commision import Commission, FreeCommission


__all__ = ["Contract"]


CommissionType = TypeVar("CommissionType", bound=Commission)


class Contract(TObject):

    _code: str = PrivateAttr()
    _exchange: str = PrivateAttr()
    _commodity: str = PrivateAttr()
    _multiplier: int = PrivateAttr()
    _margin_rate: float = PrivateAttr()
    _tick_size: float = PrivateAttr()
    _commission: CommissionType = PrivateAttr(default_factory=FreeCommission)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self._commission, dict):
            self._commission = Commission.make(**self._commission)

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
    def commission(self) -> CommissionType:
        return self._commission
    
    def calculate_notional_value(self, price: float, volume: int) -> float:
        return Formula.contract_notional_value(price, volume, self.multiplier)
    
    def calculate_margin(self, price: float, volume: int) -> float:
        return Formula.contract_margin(price, volume, self.multiplier, self.margin_rate)
