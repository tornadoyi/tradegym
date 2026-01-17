from typing import Optional, Tuple
from .trader import Trader


__all__ = ["CTPTrader"]



class CTPTrader(Trader):

    def __init__(
        self,
        cur_price_key: str,
        slippage: Optional[float] = None
    ):
        self._cur_price_key = cur_price_key
        self._slippage = slippage

    @property
    def cur_price_key(self) -> str:
        return self._cur_price_key

    @property
    def slippage(self) -> Optional[float]:
        return self._slippage
    
    def can_open(self, code: str, side: str, price: float, volume: int) -> Tuple[str, Optional[str]]:
        # check slipage price
        slip_price = self.get_slippage_price(code, "open", side)
        if not ((price >= slip_price) if side == "long" else (price <= slip_price)):
            return False, f"Current open price '{price}' is outside the allowed slippage price '{slip_price}'"
        
        # wallet
        contract = self.contract.get_contract(code)
        margin = contract.calculate_margin(price, volume)
        if not self.account.wallet.has_enough_available_cash(margin):
            return False, f"Not enough available cash, avalable cash: {self.account.wallet.available_cash}, required: {margin}"

        return True, None

    def can_close(self, code: str, side: str, price: float, volume: int) -> Tuple[str, Optional[str]]:
        # check slipage price
        slip_price = self.get_slippage_price(code, "close", side)
        if not ((price >= slip_price) if side == "short" else (price <= slip_price)):
            return False, f"Current open price '{price}' is outside the allowed slippage price '{slip_price}'"
        
        # check volume
        positions = self.account.portfolio.query(code=code, side=side, status="opened")
        total_volume = sum([p.current_volume for p in positions])
        if total_volume < volume:
            return False, f"Not enough volume, total volume: {total_volume}, required: {volume}"
        
        return True, None
        
    def open(self, code: str, side: str, price: float, volume: int) -> float:
        # check
        can_open, reason = self.can_open(code, side, price, volume)
        assert can_open, ValueError(f"Open failed, code: {code}, side: {side}, price: {price}, volume: {volume}, reason: {reason}")
        
        # commision
        contract = self.contract.get_contract(code)
        open_fee = contract.commission(
            engine=self,
            contract=self.contract.get_contract(code),
            volume=volume,
            price=price,
            trade_type="open",
            position_side=side
        )

        self.account.portfolio.open(code, side, price, volume)

    def close(self, code: str, side: str, price: float, volume: int) -> float:
        pass

    def get_slippage_price(self, code: str, trade_type: str, side: str) -> float:
        cur_price = self.kline.get_kline(code).quote[self._cur_price_key]
        slippage = 0 if self._slippage is None else self._slippage
        if (
            trade_type == "open" and side == "long" or
            trade_type == "close" and side == "short"
        ):
            cur_price += self.contract.get_contract(code).tick_size * slippage
        else:
            cur_price -= self.contract.get_contract(code).tick_size * slippage
        return cur_price
