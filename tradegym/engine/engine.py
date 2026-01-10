from typing import Optional, Sequence
from .core import PluginManager
from .account import Account
from .contract import ContractManager
from .kline import KLineManager
from .utility import Clock


__all__ = ["TradeEngine"]



class TradeEngine(PluginManager):
    def __init__(
        self,
        account: Account,
        contract: ContractManager,
        kline: KLineManager,
        clock: Optional[Clock] = None
    ):
        self.add_plugins([p for p in [account, contract, kline, clock] if p is not None])

    @property
    def clock(self) -> Clock:
        return self.get_or_create_plugin('clock')

    @property
    def account(self) -> Account:
        return self.get_or_create_plugin('account')
    
    @property
    def contract(self) -> ContractManager:
        return self.get_or_create_plugin('contract')
    
    @property
    def kline(self) -> KLineManager:
        return self.get_or_create_plugin('kline')
