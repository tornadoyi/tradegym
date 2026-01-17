from typing import Optional, Sequence, Tuple, Dict
from dataclasses import dataclass
from abc import ABC, abstractmethod
from tradegym.engine.core import Plugin
from tradegym.engine.contract import ContractManager, CommisionInfo
from tradegym.engine.kline import KLineManager
from tradegym.engine.account import Account


__all__ = ["Trader", "TradeInfo"]


@dataclass
class TradeInfo(object):
    code: str
    type: str
    side: str
    price: float
    volume: int
    commission: CommisionInfo
    success: bool
    error: Optional[str] = None
    cash_change: Optional[float] = None
    margin_change: Optional[float] = None

    def to_dict(self) -> Dict:
        d = {}
        for base_cls in type(self).mro()[::-1]:
            if not hasattr(base_cls, "__annotations__"):
                continue
            d.update({k: v  for k, v in base_cls.__annotations__.items() if v is not None})
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> CommisionInfo:
        return cls(**data)



class Trader(Plugin, ABC):
    Name: str = "trader"
    Depends: Sequence[str] = ["contract", "kline", "account"]

    @property
    def account(self) -> Account:
        return self.manager.account

    @property
    def contract(self) -> ContractManager:
        return self.manager.contract
    
    @property
    def kline(self) -> KLineManager:
        return self.manager.kline

    @abstractmethod
    def can_open(self, code: str, side: str, price: float, volume: int) -> Tuple[str, Optional[str]]:
        pass

    @abstractmethod
    def can_close(self, code: str, side: str, price: float, volume: int) -> Tuple[str, Optional[str]]:
        pass

    @abstractmethod
    def open(self, code: str, side: str, price: float, volume: int):
        pass

    @abstractmethod
    def close(self, code: str, side: str, price: float, volume: int):
        pass
    
