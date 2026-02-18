from typing import Optional, ClassVar
from tradegym.engine.core import Plugin, Field, writable
from .portfolio import Portfolio
from .wallet import Wallet


__all__ = ["Account"]


class Account(Plugin):
    Name: ClassVar[str] = "account"
    
    wallet: Wallet = Field(default_factory=lambda: Wallet(0.0))
    portfolio: Portfolio = Field(default_factory=lambda: Portfolio())
    
    def reset(self) -> None:
        self.wallet.reset()
        self.portfolio.reset()
    
   
