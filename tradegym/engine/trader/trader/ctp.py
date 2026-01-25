from typing import Optional, Tuple
from tradegym.engine.core import PrivateAttr, computed_property, Formula
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
        trade_args = {"date": self.clock.now, "code": code, "type": "open", "side": side, "price": price, "volume": volume}
        trade_args["volumes"] = [volume]

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
        commision = contract.commission(
            engine=self.engine,
            contract=contract,
            volume=volume,
            price=price,
            type="open",
            side=side
        )
        trade_args["commision"] = [commision]
        
        # wallet
        margin = trade_args["margin"] = contract.calculate_margin(price, volume)
        total_cost = commision.total_fee + margin
        if not self.account.wallet.has_enough_available_cash(total_cost):
            return TradeInfo(
                success=False,
                error=f"Not enough available cash, avalable cash: {self.account.wallet.cash}, required: {total_cost}",
                **trade_args
            )

        return TradeInfo(success=True, **trade_args)

    def try_close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> TradeInfo:
        trade_args = {"date": self.clock.now, "code": code, "type": "open", "side": side, "price": price, "volume": volume}

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
        trade_args["commisions"] = []
        trade_args["positions"] = []
        trade_args["volumes"] = []
        for position in positions:
            if total_volume == 0:
                break
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
            trade_args["commisions"].append(commision)
            trade_args["positions"].append(position.id)
            trade_args["volumes"].append(pos_volume)
        
        return TradeInfo(success=True, **trade_args)
        
    def open(self, code: str, side: str, price: float, volume: int) -> TradeInfo:
        # check
        info = self.try_open(code, side, price, volume)
        if not info.success:
            return info
        trade_args = info.to_dict()

        # apply portfolio
        pos_id = self.account.portfolio.open(
            code, side=side, price=price, volume=volume, 
            commission=info.commissions[0].total_fee, margin=info.margin, date=info.date
        )
        trade_args["positions"] = [pos_id]

        # apply wallet
        self.account.wallet.allocate_margin(margin=info.margin, commision=info.commissions[0].total_fee)
        return TradeInfo(**trade_args)

    def close(self, code: str, side: str, price: float, volume: Optional[int] = None) -> float:
        # check
        info = self.try_close(code, side, price, volume)
        if not info.success:
            return info
        assert info.positions is not None, ValueError("Invalid trade info, positions is None")
        assert info.commissions is not None, ValueError("Invalid trade info, commissions is None")
        assert info.volumes is not None, ValueError("Invalid trade info, volumes is None")
        trade_args = info.to_dict()

        contract = self.contract.get_contract(code)
        
        # apply portfolio
        trade_args["closes"] = []
        total_release_margin = total_realized_pnl = total_commision = 0.0
        for position, commision, pos_volume in zip(info.positions, info.commissions, info.volumes):
            released_margin = Formula.contract_margin(position.price, pos_volume, contract.multiplier, contract.margin_rate)
            realized_pnl = Formula.position_realized_pnl(position.price, price, pos_volume, side, contract.multiplier)
            close_id = self.account.portfolio.close(
                position.id, price=price, volume=pos_volume, commision=commision.total_fee, 
                realized_pnl=realized_pnl, released_margin=released_margin, date=info.date
            )
            trade_args["closes"].append(close_id)
            total_release_margin += realized_pnl
            total_realized_pnl += realized_pnl
            total_commision += commision.total_fee

        # apply wallet
        self.account.wallet.release_margin(margin=info.margin, pnl=total_realized_pnl, commision=total_commision)
        
        return TradeInfo(**trade_args)


    def get_slippage_price(self, code: str, type: str, side: str) -> float:
        return Formula.trade_slippage_price(
            slippage=self._slippage,
            last_price=self.kline.get_kline(code).quote[self._last_price_key],
            type=type,
            side=side,
            tick_size=self.contract.get_contract(code).tick_size
        )
