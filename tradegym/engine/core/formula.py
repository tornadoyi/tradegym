from typing import Optional


__all__ = ["Formula"]



class Formula(object):

    # ====================================== Contract ====================================== #
    @staticmethod
    def contract_notional_value(price: float, volume: int, multiplier: int) -> float:
        return price * volume * multiplier
    
    @staticmethod
    def contract_margin(price: float, volume: int, multiplier: int, margin_rate: float) -> float:
        return round(Formula.contract_notional_value(price, volume, multiplier) * margin_rate, 2)



    # ====================================== Position ====================================== #
    @staticmethod
    def position_unrealized_pnl(open_price: float, volume: int, side: str, multiplier: int, last_price: float) -> float:
        direction = +1 if side == "long" else -1
        return direction * (last_price - open_price) * volume * multiplier
    
    @staticmethod
    def position_realized_pnl(open_price: float, close_price: float, volume: int, side: str, multiplier: int, commision: float) -> float:
        direction = +1 if side == "long" else -1
        return direction * (close_price - open_price) * volume * multiplier - commision