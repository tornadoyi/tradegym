from typing import Optional, Sequence
from tradegym.engine.core import Plugin
from .portfolio import Portfolio
from .wallet import Wallet


__all__ = ["Account"]


class Account(Plugin):
    Name: str = "account"
    Depends: Sequence[str] = []

    def __init__(
        self,
        wallet: Optional[Wallet] = None,
        portfolio: Optional[Portfolio] = None,
  
    ):
        self._wallet = Wallet(0) if wallet is None else wallet
        self._portfolio = Portfolio() if portfolio is None else portfolio
    
    @property
    def wallet(self) -> Wallet:
        return self._wallet
    
    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio
    
    def to_dict(self):
        d = super().to_dict()
        d.update(
            wallet = self.wallet.to_dict(),
            portfolio = self.portfolio.to_dict()
        )
        return d
    
   
Plugin.register(Account)
