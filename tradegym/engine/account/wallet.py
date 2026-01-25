from typing import Optional, Dict
from tradegym.engine.core import TObject, PrivateAttr, computed_property


__all__ = ["Wallet", "WalletLog"]


class WalletLog(TObject):

    _reason: str = PrivateAttr()
    _cash_change: Optional[float] = PrivateAttr(None)
    _margin_change: Optional[float] = PrivateAttr(None)
    _unrealized_pnl: Optional[float] = PrivateAttr(None)

    @computed_property 
    def reason(self) -> str:
        return self._reason

    @computed_property
    def cash_change(self) -> Optional[float]:
        return self._cash_change
    
    @computed_property
    def margin_change(self) -> Optional[float]:
        return self._margin_change
    
    @computed_property
    def unrealized_pnl(self) -> Optional[float]:
        return self._unrealized_pnl



class Wallet(TObject):

    _cash: float = PrivateAttr()
    _currency: str = PrivateAttr()
    _margin: float = PrivateAttr(0.0)
    _unrealized_pnl: float = PrivateAttr(0.0)

    @computed_property
    def cash(self) -> float:
        return self._cash
    
    @computed_property
    def currency(self) -> Optional[str]:
        return self._currency
    
    @computed_property
    def margin(self) -> float:
        return self._margin
    
    @computed_property
    def unrealized_pnl(self) -> float:
        return self._unrealized_pnl
    
    @property
    def available_cash(self) -> float:
        return self.cash + self._unrealized_pnl
    
    def has_enough_available_cash(self, amount: float) -> bool:
        return self.cash + self._unrealized_pnl >= amount
    
    def adjust(
        self, 
        reason: str, 
        cash_change: Optional[float] = None, 
        margin_change: Optional[float] = None, 
        unrealized_pnl: Optional[float] = None,
    ):
        if cash_change is not None:
            self._cash += cash_change
        if margin_change is not None:
            self._margin += margin_change
        if unrealized_pnl is not None:
            self._unrealized_pnl = unrealized_pnl
        return WalletLog(reason=reason, cash_change=cash_change, margin_change=margin_change, unrealized_pnl=unrealized_pnl)