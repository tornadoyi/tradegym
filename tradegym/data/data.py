from typing import Optional
from datetime import datetime
import os
import glob
import pandas as pd
from .etl import ETL


__all__ = ['Data']


class Data(object):

    @staticmethod
    def publish(
        # io
        input_path: str,
        output_path: str,
        tick: float,

        # segment
        segment: bool = False,
        min_segment: int = 0,
        num_gap_ticks: int = 10,

        # padding
        padding: bool = False,

        # column
        dt_col: str = 'datetime',

        # performance
        num_workers: Optional[int] = None,
        complib: str = 'blosc',
        complevel: int = 9,
    ) -> None:
    
        # load input files
        input_files = [os.path.abspath(path) for path in glob.glob(input_path)]
        df = pd.concat([
            pd.read_csv(file_path)
            for file_path in input_files
        ])

        # segment
        if segment:
            dfs = ETL.segment(df, tick, num_gap_ticks, min_segment, dt_col)
        else:
            dfs = [df]

        # padding
        if padding:
            dfs = ETL.paddings(dfs, tick, dt_col, num_workers)

        # save output file
        mode = "a" if os.path.exists(output_path) else "w"
        with pd.HDFStore(output_path, mode=mode) as store:
            # load metadata
            config = store.root._v_attrs.config or {}
            num_tick_chunks = config.get(f'num_chunk_{tick}', 0)

            # save chunks
            for i, df in enumerate(dfs):
                chunk_name = f'chunk/{tick}/{num_tick_chunks + i}'
                store.put(chunk_name, df, format='table', complib=complib, complevel=complevel)
                store.get_storer(chunk_name).attrs.metadata = {
                    'start_datetime': df[dt_col].iloc[0].strftime('%Y-%m-%d %H:%M:%S'),
                    'end_datetime': df[dt_col].iloc[-1].strftime('%Y-%m-%d %H:%M:%S'),
                    'size': len(df),
                    "complib": complib,
                    "complevel": complevel,
                }

            # update metadata
            config[f'num_chunk_{tick}'] = num_tick_chunks + len(dfs)
            config["num_chunks"] = sum([v for k, v in config.items() if k.startswith("num_chunk_")])
            config.setdefault("logs", [])
            config["logs"].append({
                "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "tick": tick,
                "num_chunks": len(dfs),
            })
            store.root._v_attrs.config = config