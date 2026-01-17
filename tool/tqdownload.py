from tqsdk import TqApi, TqAuth
import argparse
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from contextlib import closing
from tqsdk.tools import DataDownloader
os.environ["TQ_SKIP_DISCLAIMER"] = "TRUE"


def parse_args():
    parser = argparse.ArgumentParser(prog='tqdownload', description="tq data downloader")
    parser.add_argument('-u', '--user', required=True, help='tq user')
    parser.add_argument('-p', '--password', required=True, help='tq password')
    parser.add_argument('-s', '--symbol', required=True, help='symbol')
    parser.add_argument('-t', '--type', required=True, choices=['day', 'tick'], help='type of data')
    parser.add_argument('-o', '--output', default=None, help='output file path')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # output path
    output_path = f"{args.symbol}.csv" if args.output is None else args.output

    # date
    year = int(f"20{args.symbol[-4:-2]}")
    month = int(args.symbol[-2:])
    start_date = datetime(year=year-1, month=month, day=1) - relativedelta(months=1)
    end_date = datetime(year=year, month=month, day=1) + relativedelta(months=1)

    pbar = tqdm(total=100)
    with closing(TqApi(auth=TqAuth(args.user, args.password))) as api:
        td = DataDownloader(
            api, symbol_list=args.symbol, dur_sec=(60 if args.type == 'day' else 0),
            start_dt=start_date, end_dt=end_date, csv_file_name=output_path
        )

        while not td.is_finished():
            api.wait_update()
            pbar.n = td.get_progress()
            pbar.refresh()


if __name__ == '__main__':
    main()