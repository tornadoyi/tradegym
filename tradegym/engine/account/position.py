from typing import Optional, Sequence, List
from datetime import datetime
import secrets
from tradegym.engine.core import TObject, PrivateAttr, computed_property
from tradegym.engine.contract import Contract


__all__ = ["Position", "Close"]


class Position(TObject):
    _code: str = PrivateAttr()
    _side: str = PrivateAttr()
    _price: float = PrivateAttr()
    _volume: float = PrivateAttr()
    _commission: float = PrivateAttr()
    _margin: float = PrivateAttr()
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
    def margin(self) -> float:
        return self._margin

    @computed_property
    def date(self) -> datetime:
        return self._date
    
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
    def closes(self) -> Sequence["Close"]:
        return self._closes
    
    @property
    def closed_commission(self) -> float:
        return sum(close.commission for close in self._closes)

    @property
    def total_commission(self) -> float:
        return self._commission + self.closed_commission

    @property
    def closed_volume(self) -> int:
        return sum(close.volume for close in self._closes)

    @property
    def current_volume(self) -> int:
        return self._volume - self.closed_volume
    
    @property
    def released_margin(self) -> float:
        return sum(close.released_margin for close in self._closes)
    
    @property
    def position_margin(self) -> float:
        return self._margin - self.released_margin

    def close(self, price: float, volume: int, commission: float, realized_pnl: float, date: datetime) -> "Close":
        assert self.current_volume >= volume, f"cannot close more than current quantity {self.current_volume}"
        close = Close(price, volume, commission, realized_pnl, date)
        self._closes.append(close)
        return close
    
    

class Close(TObject):

    _price: float = PrivateAttr()
    _volume: int = PrivateAttr()
    _commission: float = PrivateAttr()
    _released_margin: float = PrivateAttr()
    _realized_pnl: float = PrivateAttr()
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
    def released_margin(self) -> float:
        return self._released_margin

    @computed_property
    def realized_pnl(self) -> float:
        return self._realized_pnl
    
    @computed_property
    def date(self) -> datetime:
        return self._date
    