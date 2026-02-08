from typing import Sequence
import unittest
import os
import sys
import pandas as pd
from tradegym.env import TradeEnv
from tradegym.engine import Account, Wallet, ContractManager, KLineManager, CTPTrader, KLine

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CUR_DIR)

import utils


class TestKline(unittest.TestCase):
    def test_kline_run(self):
        env = self.make_env(timesteps=[0.5])
        df = pd.read_csv(os.path.join(CUR_DIR, "data", "rb2605_0805_10m_tick.csv"))
        self.assertEqual(len(df), 1199, f"{len(df)} != 1199")

        # reset
        env.reset(options={"dataframes": [df]})

        for i in range(len(df)-1):
            self.assertEqual(env.engine.kline.klines[0].cursor, i)
            obs, _, terminated, _, _ = env.step({"name": "noop"})
            if i < len(df)-2:
                self.assertFalse(terminated, f"{terminated} != False")
            else:
                self.assertTrue(terminated, f"{terminated} != True")
            
    
    def make_env(self, timesteps: Sequence[float]):
        return TradeEnv(
            account=Account(wallet=Wallet(10000)),
            contract=ContractManager([utils.CONTRACRS["rb2605"]]),
            kline=KLineManager([KLine(code="rb2605", timestep=ts) for ts in timesteps]),
            trader=CTPTrader(last_price_key="last_price"),
        )
    

if __name__ == '__main__':
    unittest.main()