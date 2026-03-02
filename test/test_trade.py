from typing import Sequence, Optional
import unittest
import os
import sys
from datetime import timedelta
import pandas as pd
from tradegym.env import TradeEnv
from tradegym.engine import Account, Wallet, ContractManager, KLineManager, CTPTrader, KLine

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CUR_DIR)

import utils


class TestTrade(unittest.TestCase):
    def test_trade_open_slippage(self):
        # load data
        df = pd.read_csv(os.path.join(CUR_DIR, "data", "rb2605_0805_10m_tick.csv"))
        tick_size = utils.CONTRACRS["rb2605"].tick_size

        # slippage = 0
        env = self.make_env(timesteps=[0.5])
        env.reset(options={"dataframes": [df]})
        quote = env.engine.kline.get_kline("rb2605").quote
        obs, _, terminated, _, _ = env.step({"name": "open", "code": "rb2605", "side": "long", "price": quote.last_price, "volume": 1})

        # slippage = 1
        env = self.make_env(timesteps=[0.5], slippage=1)
        env.reset(options={"dataframes": [df]})
        quote = env.engine.kline.get_kline("rb2605").quote
        obs, _, terminated, _, _ = env.step({"name": "open", "code": "rb2605", "side": "long", "price": quote.last_price, "volume": 1})
        self.assertFalse(obs.success, "slippage price is not correct")
        obs, _, terminated, _, _ = env.step({"name": "open", "code": "rb2605", "side": "long", "price": quote.last_price + tick_size, "volume": 1})
        self.assertTrue(obs.success, "slippage price is not correct")
            
    
    def make_env(
        self, 
        timesteps: Sequence[float], 
        slippage: Optional[float] = None
    ):
        return TradeEnv(
            account=Account(wallet=Wallet(init_cash=10000)),
            contract=ContractManager([utils.CONTRACRS["rb2605"]]),
            kline=KLineManager([KLine(code="rb2605", timestep=ts) for ts in timesteps]),
            trader=CTPTrader(last_price_key="last_price", slippage=slippage),
        )
    

if __name__ == '__main__':
    unittest.main()