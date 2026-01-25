from typing import Optional, Dict
from tradegym.engine.core import TObject, PrivateAttr, computed_property


__all__ = ["Wallet", "WalletLog"]


class Wallet(TObject):

    _cash: float = PrivateAttr()
    _currency: str = PrivateAttr()
    _margins: float = PrivateAttr(0.0)
    _unrealized_pnls: Dict[str, float] = PrivateAttr(default_factory=dict)

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
    def unrealized_pnls(self) -> Dict[str, float]:
        return self._unrealized_pnls
    
    @property
    def unrealized_pnl(self) -> float:
        return sum(self._unrealized_pnls.values())
    
    @property
    def available_cash(self) -> float:
        return self.cash + self._unrealized_pnl
    
    def has_enough_available_cash(self, amount: float) -> bool:
        return self.cash + self._unrealized_pnl >= amount
    
    def allocate_margin(self, margin: float, commision: float):
        self._cash -= (margin + commision)
        self._margin += margin

    def release_margin(self, margin: float, pnl: float, commision: float):
        self._cash += (margin + pnl - commision)
        self._margin -= margin

    def update_unrealized_pnl(self, code: str, pnl: float):
        self._unrealized_pnls[code] = pnl
        if pnl == 0:
            del self._unrealized_pnls[code]