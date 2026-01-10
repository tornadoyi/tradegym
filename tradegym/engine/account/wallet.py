from typing import Optional
from tradegym.engine.core import ISerializer


__all__ = ["Wallet"]


class Wallet(ISerializer):
    def __init__(
        self,
        available_cash: float,
        currency: str = 'CNY',
    ):
        self._available_cash = available_cash
        self._currency = currency

    @property
    def available_cash(self) -> float:
        return self._available_cash
    
    @property
    def currency(self) -> Optional[str]:
        return self._currency


    



