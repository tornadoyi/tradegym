from typing import Optional, Dict
from tradegym.engine.core import TObject, PrivateAttr, computed_property


__all__ = ["Wallet", "WalletLog"]


class WalletLog(TObject):
    _changed_cash: float = PrivateAttr()
    _changed_margin: float = PrivateAttr()

    @computed_property
    def changed_cash(self) -> float:
        return self._changed_cash
    
    @computed_property
    def changed_margin(self) -> float:
        return self._changed_margin



class Wallet(TObject):

    _cash: float = PrivateAttr()
    _currency: str = PrivateAttr()
    _margin: float = PrivateAttr(0.0)

    @computed_property
    def cash(self) -> float:
        return self._cash
    
    @computed_property
    def currency(self) -> Optional[str]:
        return self._currency
    
    @computed_property
    def margin(self) -> float:
        return self._margin
    
    def has_enough_cash(self, amount: float) -> bool:
        return self.cash >= amount
    
    def change_cash(self, amount: float) -> WalletLog:
        self._cash += amount
        return WalletLog(cash_changed=amount, margin_changed=0.0)
    
    def allocate_margin(self, amount: float) -> WalletLog:
        assert self.has_enough_cash(amount), ValueError(f"Not enough available cash, current: {self._cash}, required: {amount}")
        self._margin += amount
        self._cash -= amount
        return WalletLog(cash_changed=-amount, margin_changed=amount)

    def release_margin(self, amount: float) -> WalletLog:
        assert self.margin >= amount, ValueError(f"Not enough margin, current: {self._margin}, required: {amount}")
        self._margin -= amount
        self._cash += amount
        return WalletLog(cash_changed=amount, margin_changed=-amount)