from typing import Optional, Dict
from tradegym.engine.core import TObject
from .commission import Commission, FreeCommission


__all__ = ["Contract"]



class Contract(TObject):
    def __init__(
        self,
        code: str,
        exchange: str,
        commodity: str,
        size: int,
        margin_rate: float,
        tick_size: float,
        commission: Optional[Commission] = None,
    ):
        self._code = code
        self._exchange = exchange
        self._commodity = commodity
        self._size = size
        self._margin_rate = margin_rate
        self._tick_size = tick_size
        self._commission = FreeCommission() if commission is None else commission
    
    @property
    def code(self) -> str:
        return self._code
    
    @property
    def exchange(self) -> str:
        return self._exchange
    
    @property
    def commodity(self) -> str:
        return self._commodity
    
    @property
    def size(self) -> int:
        return self._size
    
    @property
    def margin_rate(self) -> float:
        return self._margin_rate
    
    @property
    def tick_size(self) -> float:
        return self._tick_size
    
    @property
    def commission(self) -> Commission:
        return self._commission
    
    def calculate_notional_value(self, price: float, volume: int) -> float:
        return price * self.size * volume
    
    def calculate_margin(self, price: float, volume: int) -> float:
        return round(self.calculate_notional_value(price, volume) * self.margin_rate, 2)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "exchange": self.exchange,
            "commodity": self.commodity,
            "size": self.size,
            "margin_rate": self.margin_rate,
            "commission": self._commission.to_dict()
        }
    
    def from_dict(cls, data: dict) -> "Contract":
        def make(commission: Optional[Dict] = None, **kwargs):
            return super().from_dict(
                commission=(None if commission is None else Commission.from_dict(commission))
                **kwargs, 
            )
        return make(**data)