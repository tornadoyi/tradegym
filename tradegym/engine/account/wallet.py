from typing import Optional, Dict
from dataclasses import dataclass
from tradegym.engine.core import ISerializer


__all__ = ["Wallet", "WalletLog"]


@dataclass
class WalletLog(ISerializer):
    cash_changed: float
    margin_changed: float

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__annotations__.items()}
    
    @classmethod
    def from_dict(cls, data: Dict) -> "WalletLog":
        return cls(**data)



class Wallet(ISerializer):
    def __init__(
        self,
        cash: float,
        currency: str = 'CNY',
        margin: Optional[float] = None
    ):
        self._cash = cash
        self._currency = currency
        self._margin = 0.0 if margin is None else margin

    @property
    def cash(self) -> float:
        return self._cash
    
    @property
    def currency(self) -> Optional[str]:
        return self._currency
    
    @property
    def margin(self) -> float:
        return self._margin
    
    def has_enough_cash(self, amount: float) -> bool:
        return self.cash >= amount
    
    def change_cash(self, amount: float) -> WalletLog:
        self._cash += amount
        return WalletLog(cash_changed=amount, margin_changed=0.0)
    
    def reserve_margin(self, amount: float) -> WalletLog:
        assert self.has_enough_cash(amount), ValueError(f"Not enough available cash, current: {self._cash}, required: {amount}")
        self._margin += amount
        self._cash -= amount
        return WalletLog(cash_changed=-amount, margin_changed=amount)

    def release_margin(self, amount: float) -> WalletLog:
        assert self.margin >= amount, ValueError(f"Not enough margin, current: {self._margin}, required: {amount}")
        self._margin -= amount
        self._cash += amount
        return WalletLog(cash_changed=amount, margin_changed=-amount)

    def to_dict(self):
        return {
            "cash": self.cash,
            "currency": self.currency,
            "margin": self.margin
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            cash=data["cash"],
            currency=data["currency"],
            margin=data.get("margin")
        )


    



