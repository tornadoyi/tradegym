from typing import Optional, Sequence, Tuple, ClassVar
from abc import ABC, abstractmethod
from tradegym.engine.core import Plugin, TObject, PrivateAttr, computed_property
from tradegym.engine.contract import ContractManager, CommisionInfo
from tradegym.engine.kline import KLineManager
from tradegym.engine.account import Account


__all__ = ["Trader", "TradeInfo"]


class TradeInfo(TObject):
    _code: str = PrivateAttr()
    _type: str = PrivateAttr()
    _side: str = PrivateAttr()
    _price: float = PrivateAttr()
    _volume: int = PrivateAttr()
    _commission: CommisionInfo = PrivateAttr()
    _success: bool = PrivateAttr()
    _error: Optional[str] = PrivateAttr(None)
    _cash_change: Optional[float] = PrivateAttr(None)
    _margin_change: Optional[float] = PrivateAttr(None)

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
    def commission(self) -> CommisionInfo:
        return self._commission

    @computed_property
    def success(self) -> bool:
        return self._success

    @computed_property
    def error(self) -> Optional[str]:
        return self._error

    @computed_property
    def cash_change(self) -> Optional[float]:
        return self._cash_change

    @computed_property
    def margin_change(self) -> Optional[float]:
        return self._margin_change



class Trader(Plugin, ABC):
    Name: ClassVar[str] = "trader"
    Depends: ClassVar[Sequence[str]] = ["contract", "kline", "account"]

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
    
