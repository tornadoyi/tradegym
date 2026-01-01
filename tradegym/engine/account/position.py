from typing import Optional, Sequence
from datetime import datetime
from tradegym.engine.core import TObject
from tradegym.engine.contract import Contract


__all__ = ["Position"]


class Position(TObject):
    def __init__(
        self,
        contract_code: str,
        position_type: str,
        open_price: float,
        open_quantity: int,
        open_commission: float,
        open_date: datetime,

        quantity: Optional[int] = None,
        commission: Optional[float] = None,
    ):
        assert position_type.lower() in ["long", "short"], f"invalid position_type '{position_type}', must be long or short"
        self._contract_code = contract_code
        self._contract: Optional[Contract] = None
        self._position_type = position_type.lower()

        self._open_price = open_price
        self._open_quantity = open_quantity
        self._open_commission = open_commission
        self._open_date = open_date

        self._quantity = self._open_quantity if quantity is None else quantity
        self._commission = self._open_commission if commission is None else commission
        self._closes: Sequence[Close] = []

    @property
    def contract_code(self) -> str:
        return self._contract_code
    
    @property
    def contract(self) -> Optional[Contract]:
        return self._contract
    
    @property
    def exchange_id(self) -> str:
        return self._exchange_id
    
    @property
    def position_type(self) -> str:
        return self._position_type
    
    @property
    def open_price(self) -> float:
        return self._open_price

    @property
    def open_quantity(self) -> int:
        return self._open_quantity

    @property
    def open_commission(self) -> float:
        return self._open_commission

    @property
    def open_date(self) -> datetime:
        return self._open_date
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @property
    def status(self) -> str:
        return "opened" if self._quantity > 0 else "closed"
    
    @property
    def commission(self) -> float:
        return self._commission
    
    @property
    def closes(self) -> Sequence["Close"]:
        return self._closes

    
    def setup(self, contract: Contract):
        assert contract.code == self._contract_code, f"contract code '{contract.code}' does not match position contract_code '{self._contract_code}'"
        self._contract = contract

    def close(self, price: float, quantity: int, commission: float, date: datetime):
        assert self._quantity >= quantity, f"cannot close more than current quantity {self._quantity}"
        self._quantity -= quantity
        self._commission += commission
        self._closes.append(Close(price, quantity, commission, date))

    def to_dict(self) -> dict:
        return {
            "contract_code": self._contract_code,
            "position_type": self._position_type,
            "open_price": self._open_price,
            "open_quantity": self._open_quantity,
            "open_commission": self._open_commission,
            "open_date": self._open_date.isoformat(),
            "quantity": self._quantity,
            "commission": self._commission,
            "closes": [c.to_dict() for c in self._closes]
        }


class Close(TObject):
    def __init__(
        self,
        price: float,
        quantity: int,
        commission: float,
        date: datetime
    ):
        self._price = price
        self._quantity = quantity
        self._commission = commission
        self._date = date

    @property
    def price(self) -> float:
        return self._price
    
    @property
    def quantity(self) -> int:
        return self._quantity
    
    @property
    def commission(self) -> float:
        return self._commission
    
    @property
    def date(self) -> datetime:
        return self._date
    
    def to_dict(self) -> dict:
        return {
            "price": self._price,
            "quantity": self._quantity,
            "commission": self._commission,
            "date": self._date.isoformat()
        }