from typing import Optional, Dict, TypeVar, Any
from tradegym.engine.core import TObject, Field, field_validator, Formula
from .commision import Commission, FreeCommission


__all__ = ["Contract"]


CommissionType = TypeVar("CommissionType", bound=Commission)


class Contract(TObject):

    code: str = Field()
    exchange: str = Field()
    commodity: str = Field()
    multiplier: int = Field()
    margin_rate: float = Field()
    tick_size: float = Field()
    commission: CommissionType = Field(default_factory=FreeCommission)
    
    
    @field_validator('commission', mode='plain')
    @classmethod
    def _deserialize_commission(cls, v: Any):
        assert isinstance(v, (dict, Commission)), TypeError(f"Commission must be dict or Commission, but got {type(v)}")
        if isinstance(v, Commission):
            return v
        return Commission.make(**v)

    def calculate_notional_value(self, price: float, volume: int) -> float:
        return Formula.contract_notional_value(price, volume, self.multiplier)
    
    def calculate_margin(self, price: float, volume: int) -> float:
        return Formula.contract_margin(price, volume, self.multiplier, self.margin_rate)
