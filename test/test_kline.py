from typing import Sequence
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


class TestKline(unittest.TestCase):
    def test_kline_run(self):
        env = self.make_env(timesteps=[0.5])
        df = pd.read_csv(os.path.join(CUR_DIR, "data", "rb2605_0805_10m_tick.csv"))
        self.assertEqual(len(df), 1200, f"{len(df)} != 1200")

        # reset
        env.reset(options={"dataframes": [df]})

        for i in range(len(df)-1):
            self.assertEqual(env.engine.kline.klines[0].cursor, i)
            obs, _, terminated, _, _ = env.step({"name": "noop"})
            if i < len(df)-2:
                self.assertFalse(terminated, f"env early stop")
            else:
                self.assertTrue(terminated, f"env not stop")
            
    def test_kline_missing(self):
        env = self.make_env(timesteps=[0.5])
        df = pd.read_csv(os.path.join(CUR_DIR, "data", "rb2605_0805_10m_tick.csv"))
        self.assertEqual(len(df), 1200, f"{len(df)} != 1200")
        df = df.drop([100, 101])

        # reset
        env.reset(options={"dataframes": [df]})

        for _ in range(99):
            env.step({"name": "noop"})

        q99 = env.engine.kline.klines[0].quote
        env.step({"name": "noop"})
        q100 = env.engine.kline.klines[0].quote
        env.step({"name": "noop"})
        q101 = env.engine.kline.klines[0].quote
        env.step({"name": "noop"})
        q102 = env.engine.kline.klines[0].quote
        self.assertEqual(q99.datetime, q100.datetime, f"error step in mssing data")
        self.assertEqual(q99.datetime, q101.datetime, f"error step in mssing data")
        self.assertEqual(q102.datetime - q99.datetime, timedelta(seconds=1.5), f"error step in mssing data")
        
        for i in range(102, 1200-1, 1):
            self.assertEqual(env.engine.kline.klines[0].cursor, i-2)
            self.assertEqual(env.engine.clock.now, env.engine.kline.klines[0].quote.datetime, f"kline tick error")
            obs, _, terminated, _, _ = env.step({"name": "noop"})
            if i < 1200-2:
                self.assertFalse(terminated, f"env early stop")
            else:
                self.assertTrue(terminated, f"env not stop")
        
    def test_kline_muti(self):
        env = self.make_env(timesteps=[0.5, 60])
        df_tick = pd.read_csv(os.path.join(CUR_DIR, "data", "rb2605_0805_10m_tick.csv"))
        df_minute = pd.read_csv(os.path.join(CUR_DIR, "data", "rb605_0804_0805_minute.csv"))
        
        # reset
        env.reset(options={"dataframes": [df_tick, df_minute]})

        for i in range(len(df_tick)-1):
            self.assertEqual(env.engine.kline.klines[0].cursor, i)
            self.assertEqual(env.engine.clock.now, env.engine.kline.klines[0].quote.datetime, f"kline tick error")
            self.assertGreaterEqual(env.engine.clock.now, env.engine.kline.klines[1].quote.datetime, f"kline tick error")
            self.assertLess(env.engine.clock.now - env.engine.kline.klines[1].quote.datetime, timedelta(seconds=60), f"kline tick error")

            obs, _, terminated, _, _ = env.step({"name": "noop"})
            # terminated
            if i < len(df_tick)-2:
                self.assertFalse(terminated, f"env early stop")
            else:
                self.assertTrue(terminated, f"env not stop")

    def make_env(self, timesteps: Sequence[float]):
        return TradeEnv(
            account=Account(wallet=Wallet(10000)),
            contract=ContractManager([utils.CONTRACRS["rb2605"]]),
            kline=KLineManager([KLine(code="rb2605", timestep=ts) for ts in timesteps]),
            trader=CTPTrader(last_price_key="last_price"),
        )
    

if __name__ == '__main__':
    unittest.main()