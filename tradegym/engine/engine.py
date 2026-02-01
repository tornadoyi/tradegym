from typing import Optional, Sequence
from .core import PluginManager, Plugin
from .account import Account
from .contract import ContractManager
from .kline import KLineManager
from .trader import Trader, TradeInfo
from .utility import Clock


__all__ = ["TradeEngine"]



class TradeEngine(PluginManager):

    def __init__(self,
        account: Optional[Account] = None,
        contract: Optional[ContractManager] = None,
        kline: Optional[KLineManager] = None,
        trader: Optional[Trader] = None,
        clock: Optional[Clock] = None,
        plugins: Optional[Sequence[Plugin]] = None,
    ):
        plugins = [] if plugins is None else plugins
        plugins += [p for p in [account, contract, kline, trader, clock] if p is not None]
        super().__init__(plugins=plugins)

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
    
    @property
    def trader(self) -> Trader:
        return self.get_or_create_plugin('trader')
    
    def open(self, code: str, side: str, price: float, volume: int) -> TradeInfo:
        return self.trader.open(code, side, price, volume)

    def close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> TradeInfo:
        return self.trader.close(code, side, price, volume)
