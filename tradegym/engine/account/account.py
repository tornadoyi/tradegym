from typing import Optional, Sequence, Dict
from dataclasses import dataclass
from tradegym.engine.core import Plugin, ISerializer
from .portfolio import Portfolio, PositionLog
from .wallet import Wallet, WalletLog


__all__ = ["Account", "AccountLog"]


@dataclass
class AccountLog(ISerializer):
    position: Optional[PositionLog] = None
    wallet: Optional[WalletLog] = None

    def to_dict(self) -> Dict:
        return {k: v.to_dict() for k, v in self.__annotations__.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AccountLog":
        return cls(
            position = PositionLog.from_dict(data["position"]) if "position" in data else None,
            wallet = WalletLog.from_dict(data["wallet"]) if "wallet" in data else None
        )


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
    
    def to_dict(self) -> Dict:
        d = super().to_dict()
        d.update(
            wallet = self.wallet.to_dict(),
            portfolio = self.portfolio.to_dict()
        )
        return d
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            wallet = Wallet.from_dict(data["wallet"]),
            portfolio = Portfolio.from_dict(data["portfolio"])
        )
    
   
Plugin.register(Account)
