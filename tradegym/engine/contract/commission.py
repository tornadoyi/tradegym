from typing import Optional, Dict, Type, Any
from abc import ABC, abstractmethod
import sys
from tradegym.engine.core import TObject
from tradegym.engine.engine import TradeEngine


__all__ = [
    "Commission", 
    "FreeCommission", 
    "CTPCommission"
]



class Commission(TObject, ABC):
    Name: str

    __COMMISSIONS__: Dict[str, Type["Commission"]] = {}

    @abstractmethod
    def __call__(
        self,
        engine: TradeEngine,
        contract: "Contract",
        quantity: int,
        price: float,
        trade_type: str,        # open/close
        position_type: str,     # long/short
    ):
        pass

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Commission":
        def make(name: str, **kwargs):
            return Commission.__COMMISSIONS__[name](**kwargs)
        name = data.get('name', None)
        if name not in Commission.__COMMISSIONS__:
            raise KeyError(f"commission '{name}' is not registered")
        return make(**data)

    @staticmethod
    def register(atype: Type["Commission"]):
        if atype.Name in Commission.__COMMISSIONS__:
            print(f"WARNNING commission '{atype.Name}' has been overrided by '{atype}'", file=sys.stderr)
        Commission.__COMMISSIONS__[atype.Name] = atype



class FreeCommission(Commission):
    Name: str = "free_commission"

    def __call__(self, *args, **kwargs):
        return 0




class CTPCommission(Commission):
    Name: str = "ctp_commission"

    def __init__(
        self,
        ex_open_fee: float = 0,
        ex_open_fee_rate_adv: float = 0,
        ex_close_fee : float = 0,
        ex_close_fee_today : float = 0,
        ex_close_fee_rate_adv: float = 0,
        ex_close_fee_rate_adv_today: float = 0,
        bk_open_fee: float = 0,
        bk_open_fee_rate_adv: float = 0,
        bk_close_fee : float = 0,
        bk_close_fee_today : float = 0,
        bk_close_fee_rate_adv: float = 0,
        bk_close_fee_rate_adv_today: float = 0,
    ):
        self._ex_open_fee = ex_open_fee
        self._ex_open_fee_rate_adv = ex_open_fee_rate_adv
        self._ex_close_fee = ex_close_fee
        self._ex_close_fee_today = ex_close_fee_today
        self._ex_close_fee_rate_adv = ex_close_fee_rate_adv
        self._ex_close_fee_rate_adv_today = ex_close_fee_rate_adv_today
        self._bk_open_fee = bk_open_fee
        self._bk_open_fee_rate_adv = bk_open_fee_rate_adv
        self._bk_close_fee = bk_close_fee
        self._bk_close_fee_today = bk_close_fee_today
        self._bk_close_fee_rate_adv = bk_close_fee_rate_adv
        self._bk_close_fee_rate_adv_today = bk_close_fee_rate_adv_today

    def __call__(
        self,
        engine: TradeEngine,
        contract: "Contract",
        quantity: int,
        price: float,
        trade_type: str,        # open/close
        position_type: str,     # long/short
    ):
        notional = price * contract.size * quantity

        # open
        if trade_type == "open":
            return sum([
                self._ex_open_fee * quantity,
                self._bk_open_fee * quantity,
                notional * self._ex_open_fee_rate_adv,
                notional * self._bk_open_fee_rate_adv
            ])
        
        # close
        return sum([
            self._ex_close_fee * quantity,
            self._bk_close_fee * quantity,
            notional * self._ex_close_fee_rate_adv,
            notional * self._bk_close_fee_rate_adv,
        ])



Commission.register(FreeCommission)
Commission.register(CTPCommission)