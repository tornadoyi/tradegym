from typing import Optional, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass
from tradegym.engine.core import ISerializer
from tradegym.engine.engine import TradeEngine
from tradegym.engine.account import Position


__all__ = [
    "Commission", 
    "FreeCommission", 
    "CTPCommission",
    "CommisionInfo"
]


@dataclass
class CommisionInfo(object):
    total_fee: float
    exchange_fee: Optional[float] = None
    broker_fee: Optional[float] = None

    def to_dict(self) -> Dict:
        d = {}
        for base_cls in type(self).mro()[::-1]:
            if not hasattr(base_cls, "__annotations__"):
                continue
            d.update({k: v  for k, v in base_cls.__annotations__.items() if v is not None})
        return d
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CommisionInfo":
        return cls(**data)


class Commission(ISerializer, ABC):
    Name: str

    @abstractmethod
    def __call__(
        self,
        engine: TradeEngine,
        contract: "Contract",
        price: float,
        volume: int,
        trade_type: str,        # open/close
        position: Optional[Position] = None,
    ) -> CommisionInfo:
        pass



class FreeCommission(Commission):
    Name: str = "free_commission"

    def __call__(self, *args, **kwargs):
        return CommisionInfo(total_fee=0)



class CTPCommission(Commission):
    """
    ex: exchang
    bk: broker
    adv: advanced
    """

    Name: str = "ctp_commission"

    ex_open_fee: float = 0,
    ex_open_fee_rate: float = 0,
    ex_close_fee : float = 0,
    ex_close_fee_today : float = 0,
    ex_close_fee_rate_adv: float = 0,
    ex_close_fee_rate_adv_today: float = 0,
    bk_open_fee: float = 0,
    bk_open_fee_rate: float = 0,
    bk_close_fee : float = 0,
    bk_close_fee_today : float = 0,
    bk_close_fee_rate_adv: float = 0,
    bk_close_fee_rate_adv_today: float = 0,

    def __call__(
        self,
        engine: TradeEngine,
        contract: "Contract",
        price: float,
        volume: int,
        trade_type: str,        # open/close
        position: Optional[Position] = None,
    ):
        # notional
        notional = contract.calculate_notional_value(price, volume)

        # open
        if trade_type == "open":
            exchange_fee = self.ex_open_fee * volume + notional * self.ex_open_fee_rate
            broker_fee = self.bk_open_fee * volume + notional * self.bk_open_fee_rate
            return CommisionInfo(
                total_fee=exchange_fee + broker_fee,
                exchange_fee=exchange_fee,
                broker_fee=broker_fee,
            )
        
        # close
        if engine.clock.now.day == position.open_date.day:
            ex_close_fee = self.ex_close_fee_today
            bk_close_fee = self.bk_close_fee_today
            ex_close_rate = self.ex_close_fee_rate_adv_today
            bk_close_rate = self.bk_close_fee_rate_adv_today
        else:
            ex_close_fee = self.ex_close_fee
            bk_close_fee = self.bk_close_fee
            ex_close_rate = self.ex_close_fee_rate_adv
            bk_close_rate = self.bk_close_fee_rate_adv

        exchange_fee = ex_close_fee * volume + notional * ex_close_rate
        broker_fee = bk_close_fee * volume + notional * bk_close_rate
        return CommisionInfo(
            total_fee=exchange_fee + broker_fee,
            exchange_fee=exchange_fee,
            broker_fee=broker_fee,
        )
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__annotations__.items() if k != "Name"}
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CTPCommission":
        return cls(**data)
