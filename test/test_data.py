import sys
import os
import unittest
import pandas as pd

from tradegym.data.etl import ETL

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CUR_DIR)

import utils

class TestData(unittest.TestCase):
    def test_segment(self) -> None:
        pass


    def test_align_time(self) -> None:
        df = pd.read_csv(os.path.join(CUR_DIR, "data", "badcase_test.csv"))
        df = ETL.align_time(df, 0.5)
        self.assertEqual(len(df), 3)
        self.assertEqual(df.iloc[1, 0], "2025-08-05 09:00:01.500")
        self.assertEqual(df.iloc[1, 2], 3299)


    def test_padding(self) -> None:
        df = pd.read_csv(os.path.join(CUR_DIR, "data", "badcase_test.csv"))
        df = ETL.align_time(df, 0.5)
        df = ETL.padding(df, 0.5)
        self.assertEqual(len(df), 5)
        self.assertEqual(df.iloc[0, 0], "2025-08-05 09:00:00.000")
        self.assertEqual(df.iloc[0, 2], 3296)
        self.assertEqual(df.iloc[1, 0], "2025-08-05 09:00:00.500")
        self.assertEqual(df.iloc[1, 2], 3296)
        self.assertEqual(df.iloc[2, 0], "2025-08-05 09:00:01.000")
        self.assertEqual(df.iloc[3, 0], "2025-08-05 09:00:01.500")
        self.assertEqual(df.iloc[3, 2], 3299)
        self.assertEqual(df.iloc[4, 0], "2025-08-05 09:00:02.000")
        self.assertEqual(df.iloc[4, 2], 3298)


if __name__ == '__main__':
    unittest.main()

