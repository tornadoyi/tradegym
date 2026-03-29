from typing import Optional, Sequence
import pandas as pd
from .core import PluginManager, Plugin, Formula
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

    @property
    def activated(self) -> bool:
        return self.kline.activated
    
    @property
    def terminated(self) -> bool:
        return self.kline.terminated

    def activate(self, dataframes: Sequence[pd.DataFrame]):
        self.kline.activate(dataframes)

    def reset(self):
        # reset clock
        self.clock.set_now(self.kline.calc_latest_start_time())

        # reset plugins
        super().reset()

    def tick(self):
        self.clock.tick()
        self.kline.tick()
        self.update_unrealized_pnls()

    def open(self, code: str, side: str, price: float, volume: int) -> TradeInfo:
        return self.trader.open(code, side, price, volume)

    def close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> TradeInfo:
        return self.trader.close(code, side, price, volume)

    def update_unrealized_pnls(self):
        # calculate unrealized pnls
        unrealized_pnls = {}
        for position in self.account.portfolio.opened_positions:
            contract = self.contract.get_contract(position.code)
            last_price = self.kline.get_kline(position.code).quote.last_price
            unrealized_pnls.setdefault(position.code, 0.0)
            unrealized_pnls[position.code] += Formula.position_unrealized_pnl(position.price, position.volume, position.side, contract.multiplier, last_price)
        
        # update
        for code, pnl in unrealized_pnls.items():
            self.account.wallet.update_unrealized_pnl(code, pnl)
