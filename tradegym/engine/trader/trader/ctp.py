from typing import Optional, Tuple
from tradegym.engine.core import PrivateAttr, computed_property
from tradegym.engine.contract import CommisionInfo
from .trader import Trader, TradeInfo


__all__ = ["CTPTrader"]



class CTPTrader(Trader):

    _cur_price_key: str = PrivateAttr()
    _slippage: Optional[float] = PrivateAttr(None)


    @computed_property
    def cur_price_key(self) -> str:
        return self._cur_price_key

    @computed_property
    def slippage(self) -> Optional[float]:
        return self._slippage
    
    def try_open(self, code: str, side: str, price: float, volume: int) -> TradeInfo:
        trade_args = {"code": code, "type": "open", "side": side, "price": price, "volume": volume}

        # check slipage price
        slippage_price = trade_args["slippage_price"] = self.get_slippage_price(code, "open", side)
        if not ((price >= slippage_price) if side == "long" else (price <= slippage_price)):
            return TradeInfo(
                success=False, 
                error=f"Current open price '{price}' is outside the allowed slippage price '{slippage_price}'"
                **trade_args
            )
        
        # check commision
        contract = self.contract.get_contract(code)
        commision = trade_args["commision"] = contract.commission(
            engine=self.engine,
            contract=contract,
            volume=volume,
            price=price,
            type="open",
            side=side
        )
        
        # wallet
        margin = contract.calculate_margin(price, volume)
        total_cost = commision.total_fee + margin

        if not self.account.wallet.has_enough_available_cash(total_cost):
            return TradeInfo(
                success=False,
                error=f"Not enough available cash, avalable cash: {self.account.wallet.cash}, required: {total_cost}",
                **trade_args
            )

        return TradeInfo(success=True, **trade_args)

    def try_close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> TradeInfo:
        trade_args = {"code": code, "type": "open", "side": side, "price": price, "volume": volume}

        # check volume
        positions = self.account.portfolio.query(code=code, side=side, status="opened")
        total_volume = sum([p.current_volume for p in positions])
        if volume is None:
            volume = trade_args["volume"] = total_volume
        if total_volume < volume:
            return TradeInfo(
                success=False, 
                error=f"Current close price '{price}' is outside the allowed slippage price '{slippage_price}'"
                **trade_args
            )

        # check slipage price
        slippage_price = self.get_slippage_price(code, "close", side)
        if not ((price >= slippage_price) if side == "short" else (price <= slippage_price)):
            return TradeInfo(
                success=False, 
                error=f"Current close price '{price}' is outside the allowed slippage price '{slippage_price}'"
                **trade_args
            )
        
        # check commision
        contract = self.contract.get_contract(code)
        exchange_fee = broker_fee = 0
        for position in positions:
            pos_volume = min(total_volume, position.current_volume)
            total_volume -= pos_volume
            commision = contract.commission(
                engine=self.engine,
                contract=contract,
                volume=pos_volume,
                price=price,
                type="close",
                side=side
            )
            exchange_fee += commision.exchange_fee
            broker_fee += commision.broker_fee

        commision = trade_args["commision"] = CommisionInfo(exchange_fee=exchange_fee, broker_fee=broker_fee)
        
        return TradeInfo(success=True, **trade_args)
        
    def open(self, code: str, side: str, price: float, volume: int) -> float:
        # check
        pass

    def close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> float:
        pass

    def get_slippage_price(self, code: str, type: str, side: str) -> float:
        cur_price = self.kline.get_kline(code).quote[self._cur_price_key]
        slippage = 0 if self._slippage is None else self._slippage
        if (
            type == "open" and side == "long" or
            type == "close" and side == "short"
        ):
            cur_price += self.contract.get_contract(code).tick_size * slippage
        else:
            cur_price -= self.contract.get_contract(code).tick_size * slippage
        return cur_price
