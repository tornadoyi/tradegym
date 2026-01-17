from typing import Optional, Sequence, List, Dict
from dataclasses import dataclass
from datetime import datetime
import secrets
from tradegym.engine.core import ISerializer
from tradegym.engine.contract import Contract


__all__ = ["Position", "PositionLog"]


class Position(ISerializer):
    def __init__(
        self,
        code: str,
        side: str,
        price: float,
        volume: int,
        commission: float,
        date: datetime,
        id: Optional[str] = None,
    ):
        assert side.lower() in ["long", "short"], f"invalid side '{side}', must be long or short"
        self._id = secrets.token_urlsafe(8) if id is None else id
        self._code = code
        self._contract: Optional[Contract] = None
        self._side = side.lower()

        self._open_price = price
        self._open_volume = volume
        self._open_commission = commission
        self._open_date = date

        self._closes: List[Close] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def code(self) -> str:
        return self._code
    
    @property
    def contract(self) -> Optional[Contract]:
        return self._contract
    
    @property
    def side(self) -> str:
        return self._side
    
    @property
    def open_price(self) -> float:
        return self._open_price

    @property
    def open_volume(self) -> int:
        return self._open_volume

    @property
    def open_commission(self) -> float:
        return self._open_commission

    @property
    def open_date(self) -> datetime:
        return self._open_date
    
    @property
    def current_volume(self) -> int:
        return self._open_volume - sum(close.volume for close in self._closes)
    
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
        return self._open_commission + sum(close.commission for close in self._closes)
    
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

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "code": self._code,
            "side": self._side,
            "price": self._open_price,
            "volume": self._open_volume,
            "commission": self._open_commission,
            "date": self._open_date.isoformat(),
            "closes": [c.to_dict() for c in self._closes]
        }


class Close(ISerializer):
    def __init__(
        self,
        price: float,
        volume: int,
        commission: float,
        date: datetime,
        id: Optional[str] = None
    ):
        self._id = secrets.token_urlsafe(8) if id is None else id
        self._price = price
        self._volume = volume
        self._commission = commission
        self._date = date

    @property
    def id(self) -> str:
        return self._id

    @property
    def price(self) -> float:
        return self._price
    
    @property
    def volume(self) -> int:
        return self._volume
    
    @property
    def commission(self) -> float:
        return self._commission
    
    @property
    def date(self) -> datetime:
        return self._date
    
    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "price": self._price,
            "volume": self._volume,
            "commission": self._commission,
            "date": self._date.isoformat()
        }
    

@dataclass
class PositionLog(ISerializer):
    id: str
    type: str
    side: str
    price: float
    volume: int
    date: datetime
    close_id: Optional[str] = None

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__annotations__.items()}
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PositionLog":
        return cls(**data)