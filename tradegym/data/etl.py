from concurrent.futures import as_completed
from typing import Optional, List
from concurrent.futures import ProcessPoolExecutor
import os
import pandas as pd
from tqdm import tqdm


__all__ = ['ETL']


class ETL(object):

    @staticmethod
    def segment(
        df: pd.DataFrame,
        tick: float,
        num_gap_ticks: int = 10,
        min_segment: int = 0,
        dt_col: str = 'datetime',
    ) -> List[pd.DataFrame]:

        # convert datetime
        df[dt_col] = pd.to_datetime(df[dt_col])

        # sort
        df = df.sort_values(dt_col).reset_index(drop=True)

        # find segments
        time_diffs = df[dt_col].diff()
        gap_mask = time_diffs > pd.Timedelta(seconds=tick * num_gap_ticks)
        segment_starts = [0] + df.index[gap_mask].tolist()
        segments: List[pd.DataFrame] = []
        for i in range(1, len(segment_starts), 1):
            st, ed = segment_starts[i-1], segment_starts[i]
            if ed - st < min_segment:
                continue 
            segments.append(df.iloc[st:ed].reset_index(drop=True))
        return segments


    @staticmethod
    def paddings(
        dfs: List[pd.DataFrame],
        tick: float,
        dt_col: str = 'datetime',
        num_workers: Optional[int] = None,
    ) -> List[pd.DataFrame]:
        if num_workers is None:
            num_workers = os.cpu_count()
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {executor.submit(ETL.padding, df, tick, dt_col): i for i, df in enumerate(dfs)}
            results = [None] * len(dfs)
            for future in tqdm(as_completed(futures), total=len(dfs), desc='Padding'):
                idx = futures[future]
                results[idx] = future.result()
            return results

    
    @staticmethod
    def padding(
        df: pd.DataFrame,
        tick: float,
        dt_col: str = 'datetime',
    ) -> pd.DataFrame:
        # padding
        full_range = pd.date_range(start=df[dt_col].iloc[0], end=df[dt_col].iloc[-1], freq=f'{tick}s')
        filled = pd.DataFrame({dt_col: full_range})
        merged = filled.merge(df, on=dt_col, how='left')

        # add padding flag
        merged = merged.sort_values(dt_col).reset_index(drop=True)
        merged['padding'] = ~merged[dt_col].isin(df[dt_col])

        # fill missing values
        for col in merged.columns:
            if col != dt_col and col != 'padding' and merged[col].isna().any():
                merged[col] = merged[col].ffill()
        return merged