from typing import Optional, Sequence, List, Dict
from datetime import datetime
import secrets
from tradegym.engine.core import TObject, PrivateAttr, computed_property, Formula
from tradegym.engine.contract import Contract


__all__ = ["Position", "Close"]


class Position(TObject):
    _code: str = PrivateAttr()
    _side: str = PrivateAttr()
    _price: float = PrivateAttr()
    _volume: float = PrivateAttr()
    _commission: float = PrivateAttr()
    _date: datetime = PrivateAttr()

    _id: str = PrivateAttr(default_factory=lambda: secrets.token_urlsafe(8))
    _contract: Optional[Contract] = PrivateAttr(None)
    _closes: List["Close"] = PrivateAttr(default_factory=list)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self._side in ["long", "short"], f"invalid side '{self._side}', must be long or short"

    @computed_property
    def id(self) -> str:
        return self._id

    @computed_property
    def code(self) -> str:
        return self._code
    
    @property
    def contract(self) -> Optional[Contract]:
        return self._contract
    
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
    def commission(self) -> float:
        return self._commission

    @computed_property
    def date(self) -> datetime:
        return self._date
    
    @property
    def current_volume(self) -> int:
        return self._volume - sum(close.volume for close in self._closes)
    
    @property
    def status(self) -> str:
        return "opened" if self.current_volume > 0 else "closed"
    
    @property
    def opened(self) -> bool:
        return self.status == "opened"
    
    @property
    def closed(self) -> bool:
        return self.status == "closed"
    
    @property
    def total_commission(self) -> float:
        return self._commission + sum(close.commission for close in self._closes)
    
    @property
    def closes(self) -> Sequence["Close"]:
        return self._closes

    def setup(self, contract: Contract):
        assert contract.code == self._code, f"contract code '{contract.code}' does not match position contract_code '{self._code}'"
        self._contract = contract

    def close(self, price: float, volume: int, commission: float, date: datetime) -> "Close":
        assert self.current_volume >= volume, f"cannot close more than current quantity {self.current_volume}"
        close = Close(price, volume, commission, date)
        self._closes.append(close)
        return close
    
    def calculate_realized_pnl(self) -> float:
        return sum([
            Formula.position_realized_pnl(self._price, close.price, close.volume, self._side, self._contract.multiplier, close.commission)
            for close in self._closes 
        ]) -self._commission
    
    def calculate_unrealized_pnl(self, last_price: float) -> float:
        return Formula.position_unrealized_pnl(self._price, self.current_volume, self._side, self._contract.multiplier, last_price)

    

class Close(TObject):

    _price: float = PrivateAttr()
    _volume: int = PrivateAttr()
    _commission: float = PrivateAttr()
    _date: datetime = PrivateAttr()
    _id: str = PrivateAttr(default_factory=lambda: secrets.token_urlsafe(8))

    @computed_property
    def id(self) -> str:
        return self._id

    @computed_property
    def price(self) -> float:
        return self._price
    
    @computed_property
    def volume(self) -> int:
        return self._volume
    
    @computed_property
    def commission(self) -> float:
        return self._commission
    
    @computed_property
    def date(self) -> datetime:
        return self._date
    