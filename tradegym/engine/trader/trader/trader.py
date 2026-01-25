from typing import Optional, Sequence, List, ClassVar
from datetime import datetime
from abc import ABC, abstractmethod
from tradegym.engine.core import Plugin, TObject, PrivateAttr, computed_property
from tradegym.engine.contract import ContractManager, CommisionInfo
from tradegym.engine.kline import KLineManager
from tradegym.engine.account import Account, AccountLog
from tradegym.engine.utility import Clock


__all__ = ["Trader", "TradeInfo"]


class TradeInfo(TObject):
    _date: datetime = PrivateAttr()
    _code: str = PrivateAttr()
    _type: str = PrivateAttr()
    _side: str = PrivateAttr()
    _price: float = PrivateAttr()
    _success: bool = PrivateAttr()
    _error: Optional[str] = PrivateAttr(None)
    _volume: Optional[None] = PrivateAttr(None)
    _slippage_price: Optional[float] = PrivateAttr(None)
    _margin: Optional[float] = PrivateAttr(None)
    
    _commissions: Optional[List[CommisionInfo]] = PrivateAttr(None)
    _volumes: Optional[List[int]] = PrivateAttr(None)
    _positions: Optional[List[str]] = PrivateAttr(None)
    _closes: Optional[List[str]] = PrivateAttr(None)
    _account: Optional[AccountLog] = PrivateAttr(None)

    @computed_property
    def date(self) -> datetime:
        return self._date

    @computed_property
    def code(self) -> str:
        return self._code
    
    @computed_property
    def type(self) -> str:
        return self._type

    @computed_property
    def side(self) -> str:
        return self._side

    @computed_property
    def price(self) -> float:
        return self._price

    @computed_property
    def volume(self) -> int:
        return self._volume
    
    @computed_property
    def success(self) -> bool:
        return self._success
    
    @computed_property
    def error(self) -> Optional[str]:
        return self._error
    
    @computed_property
    def slippage_price(self) -> Optional[float]:
        return self._slippage_price
    
    @computed_property
    def margin(self) -> Optional[float]:
        return self._margin

    @computed_property
    def commissions(self) -> Optional[List[CommisionInfo]]:
        return self._commissions

    @computed_property
    def positions(self) -> Optional[List[str]]:
        return self._positions
    
    @computed_property
    def closes(self) -> Optional[List[str]]:
        return self._closes
    
    @computed_property  
    def volumes(self) -> Optional[List[int]]:
        return self._volumes

    @computed_property
    def account(self) -> Optional[AccountLog]:
        return self._account




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
    
