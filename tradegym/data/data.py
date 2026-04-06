from typing import Optional
import yaml
from datetime import datetime
import os
import glob
import pandas as pd
from tradegym.core import logging
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
        logging.info(f"Loaded {len(input_files)} files from {input_path}")
        df = pd.concat([
            pd.read_csv(file_path)
            for file_path in input_files
        ])
        logging.info(f"Loaded {len(df)} rows from {len(input_files)} files")

        # normalize columns
        df = ETL.normalize_columns(df)
        logging.info(f"Normalized columns: {df.columns}")

        # drop nan
        df_dropped = df.dropna()
        logging.info(f"Dropped {len(df) - len(df_dropped)} rows with nan")
        df = df_dropped

        # segment
        if segment:
            dfs = ETL.segment(df, tick, num_gap_ticks, min_segment, dt_col)
        else:
            dfs = [df]
        logging.info(f"Segmented {len(dfs)} chunks")

        # padding
        if padding:
            dfs = ETL.paddings(dfs, tick, dt_col, num_workers)
        logging.info(f"Padded {len(dfs)} chunks")

        # save output file
        output_path = os.path.abspath(output_path)
        mode = "a" if os.path.exists(output_path) else "w"
        with pd.HDFStore(output_path, mode=mode) as store:
            # load metadata
            config = getattr(store.root._v_attrs, "config", {})
            num_chunks = config.get(f'num_chunks', 0)

            # save chunks
            for i, df in enumerate(dfs):
                chunk_name = f'chunk/df_{num_chunks + i}'
                store.put(chunk_name, df, format='table', complib=complib, complevel=complevel)
                store.get_storer(chunk_name).attrs.metadata = {
                    'tick': tick,
                    'start_datetime': df[dt_col].iloc[0].strftime('%Y-%m-%d %H:%M:%S'),
                    'end_datetime': df[dt_col].iloc[-1].strftime('%Y-%m-%d %H:%M:%S'),
                    'size': len(df),
                    "complib": complib,
                    "complevel": complevel,
                }

            # update metadata
            config["num_chunks"] = num_chunks + len(dfs)
            config.setdefault("logs", [])
            config["logs"].append({
                "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "tick": tick,
                "num_chunks": len(dfs),
            })
            store.root._v_attrs.config = config

        logging.info(f"Published to {output_path}")

    
    @staticmethod
    def show(input_path: str, index: Optional[int] = None) -> None:
        with pd.HDFStore(input_path, 'r') as store:
            if index is None:
                config = getattr(store.root._v_attrs, "config", {})
                logging.info("\n" + yaml.dump(config, sort_keys=False))
            else:
                chunk_name = f'chunk/df_{index}'
                metadata = store.get_storer(chunk_name).attrs.metadata
                logging.info("\n" + yaml.dump(metadata, sort_keys=False))

    @staticmethod
    def export(
        input_path: str, 
        index: int,
        output_path: Optional[str] = None,
    ) -> None:

        if output_path is None:
            output_path = f'chunk_{index}.csv'
        output_path = os.path.abspath(output_path)

        with pd.HDFStore(input_path, 'r') as store:
            chunk_name = f'chunk/df_{index}'
            df = store.get(chunk_name)
            df.to_csv(output_path, index=False)
        logging.info(f"Exported chunk {index} to {output_path}")

            