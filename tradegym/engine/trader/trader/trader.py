from typing import Optional, Sequence, Tuple, ClassVar
from abc import ABC, abstractmethod
from tradegym.engine.core import Plugin, TObject, PrivateAttr, computed_property
from tradegym.engine.contract import ContractManager, CommisionInfo
from tradegym.engine.kline import KLineManager
from tradegym.engine.account import Account, AccountLog


__all__ = ["Trader", "TradeInfo"]


class TradeInfo(TObject):
    _code: str = PrivateAttr()
    _type: str = PrivateAttr()
    _side: str = PrivateAttr()
    _price: float = PrivateAttr()
    _success: bool = PrivateAttr()
    _volume: Optional[None] = PrivateAttr(None)
    _slippage_price: Optional[float] = PrivateAttr(None)
    _commission: Optional[CommisionInfo] = PrivateAttr(None)
    _error: Optional[str] = PrivateAttr(None)
    _account: Optional[AccountLog] = PrivateAttr(None)

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
    def slippage_price(self) -> Optional[float]:
        return self._slippage_price

    @computed_property
    def commission(self) -> Optional[CommisionInfo]:
        return self._commission

    @computed_property
    def error(self) -> Optional[str]:
        return self._error

    @computed_property
    def account(self) -> Optional[AccountLog]:
        return self._account




class Trader(Plugin, ABC):
    Name: ClassVar[str] = "trader"
    Depends: ClassVar[Sequence[str]] = ["contract", "kline", "account"]

    @property
    def engine(self) -> "TradeEngine":
        return self.manager

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
    def open(self, code: str, side: str, price: float, volume: int):
        pass

    @abstractmethod
    def close(self, code: str, side: str, price: float, volume: Optional[int] = None):
        pass
    
