from typing import Optional, Dict, ClassVar
from abc import ABC, abstractmethod
from tradegym.engine.core import TObject, PrivateAttr, computed_property
from tradegym.engine.engine import TradeEngine
from tradegym.engine.account import Position


__all__ = [
    "Commission", 
    "FreeCommission", 
    "CTPCommission",
    "CommisionInfo"
]



class CommisionInfo(TObject):
    _exchange_fee: Optional[float] = PrivateAttr(None)
    _broker_fee: Optional[float] = PrivateAttr(None)

    @computed_property
    def total_fee(self) -> float:
        return (self._exchange_fee or 0) + (self._broker_fee or 0)
    
    @computed_property
    def exchange_fee(self) -> Optional[float]:
        return self._exchange_fee
    
    @computed_property
    def broker_fee(self) -> Optional[float]:
        return self._broker_fee
    


class Commission(TObject, ABC):
    Name: ClassVar[str]

    @abstractmethod
    def __call__(
        self,
        engine: TradeEngine,
        contract: "Contract",
        price: float,
        volume: int,
        type: str,        # open/close
        side: str,
        position: Optional[Position] = None,
    ) -> CommisionInfo:
        pass



class FreeCommission(Commission):
    Name: ClassVar[str] = "free_commission"

    def __call__(self, *args, **kwargs) -> CommisionInfo:
        return CommisionInfo(total_fee=0)



