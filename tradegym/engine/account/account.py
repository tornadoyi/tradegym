from typing import Optional, Sequence, Dict, ClassVar
from tradegym.engine.core import Plugin, PrivateAttr, computed_property
from .portfolio import Portfolio
from .wallet import Wallet


__all__ = ["Account", "AccountLog"]


class Account(Plugin):
    Name: ClassVar[str] = "account"
    
    _wallet: Wallet = PrivateAttr(default_factory=lambda: Wallet(0.0))
    _portfolio: Portfolio = PrivateAttr(default_factory=lambda: Portfolio())

    @computed_property
    def wallet(self) -> Wallet:
        return self._wallet
    
    @computed_property
    def portfolio(self) -> Portfolio:
        return self._portfolio
    
   
Plugin.register(Account)
