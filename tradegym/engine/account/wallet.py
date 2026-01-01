from typing import Optional
from tradegym.engine.core import TObject


__all__ = ["Wallet"]


class Wallet(TObject):
    def __init__(
        self,
        available_cash: float,
        currency: str = 'CNY',
        margin_used: float = 0,
    ):
        self._available_cash = available_cash
        self._margin_used = margin_used
        self._currency = currency

    @property
    def available_cash(self) -> float:
        return self._available_cash
    
    @property
    def currency(self) -> Optional[str]:
        return self._currency
    
    @property
    def margin_used(self) -> float:
        return self._margin_used

    



