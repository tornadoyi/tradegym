import os
from datetime import timedelta
import pandas as pd
from tradegym.env import TradeEnv
from tradegym.engine import Account, Wallet, Contract, ContractManager, KLineManager, CTPTrader, KLine, CTPCommission, Clock


CUR_DIR = os.path.dirname(os.path.abspath(__file__))


CONTRACRS = {
    "rb2605": Contract(
        code="rb2605",
        commodity="螺纹钢",
        exchange="SHFE",
        multiplier=10,
        tick_size=1.0,
        margin_rate=0.13,
        commission=CTPCommission(
            ex_open_fee_rate = 0.0001,
            ex_close_fee_rate = 0.0001,
            ex_close_fee_rate_adv = 0.0001,
            bk_open_fee = 0.01,
            bk_close_fee = 0.01,
            bk_close_fee_adv = 0.01,
        )
    )
}


def make_env(cash=10000):
    df_tick = pd.read_csv(os.path.join(CUR_DIR, "data", "SHFE.rb2605.0805am.tick.csv"))
    df_minute = pd.read_csv(os.path.join(CUR_DIR, "data", "SHFE.rb2605.8m.minute.csv"))
    
    return TradeEnv(
        account=Account(wallet=Wallet(cash)),
        contract=ContractManager([CONTRACRS["rb2605"]]),
        kline=KLineManager([
            KLine(code="rb2605", timestep=0.5),
            KLine(code="rb2605", timestep=1.0),
        ]),
        trader=CTPTrader(last_price_key="last_price"),
        clock=Clock(step=timedelta(seconds=0.5))
    )