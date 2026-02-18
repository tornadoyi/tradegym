from typing import ClassVar, Optional
from tradegym.engine.core import Field
from tradegym.engine.contract.contract import Contract
from .commission import Commission, CommisionInfo


__all__ = ["CTPCommission"]


class CTPCommission(Commission):
    """
    ex: exchang
    bk: broker
    adv: advanced
    """

    Name: ClassVar[str] = "ctp_commission"

    ex_open_fee: float = Field(0)
    ex_open_fee_rate: float = Field(0)
    ex_close_fee : float = Field(0)
    ex_close_fee_adv : float = Field(0)
    ex_close_fee_rate: float = Field(0)
    ex_close_fee_rate_adv: float = Field(0)
    bk_open_fee: float = Field(0)
    bk_open_fee_rate: float = Field(0)
    bk_close_fee : float = Field(0)
    bk_close_fee_adv : float = Field(0)
    bk_close_fee_rate: float = Field(0)
    bk_close_fee_rate_adv: float = Field(0)


    def __call__(
        self,
        engine: "TradeEngine",
        contract: Contract,
        price: float,
        volume: int,
        type: str,        # open/close
        side: str,
        position: Optional["Position"] = None,
    ) -> CommisionInfo:
        # notional
        notional = contract.calculate_notional_value(price, volume)

        # open
        if type == "open":
            exchange_fee = self.ex_open_fee * volume + notional * self.ex_open_fee_rate
            broker_fee = self.bk_open_fee * volume + notional * self.bk_open_fee_rate
            return CommisionInfo(
                exchange_fee=exchange_fee,
                broker_fee=broker_fee,
            )
        
        assert position is not None, ValueError("position is None for close")
        # close
        if engine.clock.now.day == position.date.day:
            ex_close_fee = self.ex_close_fee
            bk_close_fee = self.bk_close_fee
            ex_close_rate = self.ex_close_fee_rate
            bk_close_rate = self.bk_close_fee_rate
        else:
            ex_close_fee = self.ex_close_fee_adv
            bk_close_fee = self.bk_close_fee_adv
            ex_close_rate = self.ex_close_fee_rate_adv
            bk_close_rate = self.bk_close_fee_rate_adv

        exchange_fee = ex_close_fee * volume + notional * ex_close_rate
        broker_fee = bk_close_fee * volume + notional * bk_close_rate
        return CommisionInfo(
            exchange_fee=exchange_fee,
            broker_fee=broker_fee,
        )
    
