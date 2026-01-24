from typing import Optional, Sequence, Dict, ClassVar
from tradegym.engine.core import Plugin, TObject, PrivateAttr, computed_property
from .portfolio import Portfolio, PositionLog
from .wallet import Wallet, WalletLog


__all__ = ["Account", "AccountLog"]


class AccountLog(TObject):
    _position: Optional[PositionLog] = PrivateAttr(None)
    _wallet: Optional[WalletLog] = PrivateAttr(None)

    @computed_property
    def position(self) -> Optional[PositionLog]:
        return self._position
    
    @computed_property
    def wallet(self) -> Optional[WalletLog]:
        return self._wallet



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
    
    def open(self, margin: float, **kwargs) -> AccountLog:
        w_log = self.wallet.allocate_margin(margin)
        p_log = self.portfolio.open(**kwargs)
        return AccountLog(position=p_log, wallet=w_log)

    

    
   
Plugin.register(Account)
