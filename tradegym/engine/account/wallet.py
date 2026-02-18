from typing import Optional, Dict
from tradegym.engine.core import TObject, Field, writable


__all__ = ["Wallet"]


class Wallet(TObject):
    init_cash: float = Field()
    cash: float = Field(None)
    currency: str = Field("CNY")
    margin: float = Field(0.0)
    unrealized_pnls: Dict[str, float] = Field(default_factory=dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.cash is None:
            with self.writable():
                self.cash = self.init_cash

    @property
    def unrealized_pnl(self) -> float:
        return sum(self.unrealized_pnls.values())
    
    @property
    def available_cash(self) -> float:
        return self.cash + self.unrealized_pnl
    
    @writable
    def reset(self):
        self.cash = self.init_cash
        self.margin = 0.0
        self.unrealized_pnls = {}

    def has_enough_available_cash(self, amount: float) -> bool:
        return self.cash + self.unrealized_pnl >= amount
    
    @writable
    def allocate_margin(self, margin: float, commision: float):
        self.cash -= (margin + commision)
        self.margin += margin

    @writable
    def release_margin(self, margin: float, pnl: float, commision: float):
        self.cash += (margin + pnl - commision)
        self.margin -= margin

    @writable
    def update_unrealized_pnl(self, code: str, pnl: float):
        self.unrealized_pnls[code] = pnl
        if pnl == 0:
            del self.unrealized_pnls[code]