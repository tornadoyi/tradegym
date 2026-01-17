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
    
    def open(self, code: str, side: str, price: float, volume: int) -> None:
        contract = self.contract.get_contract(code)

        # tick size check
        if not (abs(price / contract.tick_size - round(price / contract.tick_size)) < 1e-9):
            raise ValueError(f"price {price} is not a valid price for {code}, tick size is {contract.tick_size}")

        # open
        open_cash = price * volume * contract.size * volume

        # calculate commision
        open_fee = contract.commission(self, contract=contract, volume=volume, price=price, trade_type='open', position_side=side)


    def close(self, code: str, side: str, price: float, volume: int) -> None:
        pass
