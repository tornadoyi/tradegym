from typing import Optional, Sequence, List, ClassVar
from datetime import datetime
from abc import ABC, abstractmethod
from tradegym.engine.core import Plugin, TObject, Field
from tradegym.engine.contract import ContractManager, CommisionInfo
from tradegym.engine.kline import KLineManager
from tradegym.engine.account import Account
from tradegym.engine.utility import Clock


__all__ = ["Trader", "TradeInfo"]


class TradeInfo(TObject):
    date: datetime = Field()
    code: str = Field()
    type: str = Field()
    side: str = Field()
    price: float = Field()
    success: bool = Field()
    error: Optional[str] = Field(None)
    volume: Optional[int] = Field(None)
    slippage_price: Optional[float] = Field(None)
    margin: Optional[float] = Field(None)
    
    commissions: Optional[List[CommisionInfo]] = Field(None)
    volumes: Optional[List[int]] = Field(None)
    positions: Optional[List[str]] = Field(None)
    closes: Optional[List[str]] = Field(None)

    

class Trader(Plugin, ABC):
    Name: ClassVar[str] = "trader"
    Depends: ClassVar[Sequence[str]] = ["contract", "kline", "account", "clock"]

    @property
    def engine(self) -> "TradeEngine":
        return self.manager
    
    @property
    def clock(self) -> Clock:
        return self.engine.clock

    @property
    def account(self) -> Account:
        return self.engine.account

    @property
    def contract(self) -> ContractManager:
        return self.engine.contract
    
    @property
    def kline(self) -> KLineManager:
        return self.engine.kline

    @abstractmethod
    def try_open(self, code: str, side: str, price: float, volume: int) -> TradeInfo:
        pass

    @abstractmethod
    def try_close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> TradeInfo:
        pass

    @abstractmethod
    def open(self, code: str, side: str, price: float, volume: int) -> TradeInfo:
        pass

    @abstractmethod
    def close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> TradeInfo:
        pass
    
