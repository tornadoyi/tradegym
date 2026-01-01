from typing import Optional, Sequence
from .core import TObject, Clock
from .account import Account
from .contract import Contract


__all__ = ["TradeEngine"]



class TradeEngine(TObject):
    def __init__(
        self,
        account: Account,
        contracts: Sequence[Contract],
        clock: Optional[Clock] = None
    ):
        self._account = account
        self._contracts = contracts

        # clock
        self._clock = Clock() if clock is None else clock

    @property
    def clock(self) -> Clock:
        return self._clock

    @property
    def account(self) -> Account:
        return self._account