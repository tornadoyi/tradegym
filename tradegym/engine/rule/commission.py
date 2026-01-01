from typing import Optional
from abc import ABC, abstractmethod
from tradegym.engine.core import TObject, Contract
from tradegym.engine.engine import TradeEngine
from .rule import Rule


__all__ = ["Commission"]



class Commission(Rule, ABC):

    @abstractmethod
    def __call__(
        self,
        engine: TradeEngine,
        contract: Contract,
        quantity: int,
        price: float,
        trade_type: str,        # open/close
        position_type: str,     # long/short
    ):
        pass
