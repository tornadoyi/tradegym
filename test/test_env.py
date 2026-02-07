import unittest
import os
import sys
from tradegym.env import TradeEnv

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CUR_DIR)

import utils


class TestEnv(unittest.TestCase):
    def test_env_copy(self):
        env = utils.make_env(cash=10000)
        data = env.to_dict()
        env = TradeEnv.from_dict(data)
        data2 = env.to_dict()
        self.assertDictEqual(data, data2)
    
    def test_env_reset(self):
        data = utils.get_data()
        env = utils.make_env(cash=10000)
        env.reset(options={"dataframes": [data['tick'], data['minute']]})


if __name__ == '__main__':
    unittest.main()