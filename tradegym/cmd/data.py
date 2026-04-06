import argparse
from tradegym.data import Data


__all__ = ['add_parser']


def add_parser(sparser: argparse._SubParsersAction):
    parser = sparser.add_parser('data', help='data processing commands')
    sparser = parser.add_subparsers()

    # publish
    parser = sparser.add_parser('publish', help='publish csv to traning data')
    parser.set_defaults(func=async_publush)
    parser.add_argument('input', type=str, help='input csv path')
    parser.add_argument('-o', '--output', type=str, required=True, help='output training data path')
    parser.add_argument('--tick', type=float, required=True, help='tick (0.5/60/3600)')

    parser.add_argument('--segment', action='store_true', default=False, help='segment data')
    parser.add_argument('--min-segment', type=int, default=0, help='min segment size')
    parser.add_argument('--num-gap-ticks', type=int, default=10, help='number of gap ticks')

    parser.add_argument('--padding', action='store_true', help='padding data')

    parser.add_argument('--dt-col', type=str, default='datetime', help='datetime column name')

    parser.add_argument('--num-workers', type=int, default=None, help='number of workers to processing log data')
    parser.add_argument('--complib', type=str, default='blosc', help='compression library')
    parser.add_argument('--complevel', type=int, default=9, help='compression level')
    
    # show
    parser = sparser.add_parser('show', help='show metadata of published data')
    parser.set_defaults(func=async_show)
    parser.add_argument('input', type=str, help='input data path')
    parser.add_argument('-i', '--index', type=int, default=None, help='index of chunk')

    # export
    parser = sparser.add_parser('export', help='export dataframe from published data')
    parser.set_defaults(func=async_export)
    parser.add_argument('-i', '--input', type=str, required=True, help='input data path')
    parser.add_argument('-o', '--output', type=str, required=True, help='output dataframe path')
    parser.add_argument('-c', '--chunk', type=str, required=True, help='chunk name')


async def async_publush(args):
    Data.publish(
        input_path=args.input,
        output_path=args.output,
        tick=args.tick,
        segment=args.segment,
        min_segment=args.min_segment,
        num_gap_ticks=args.num_gap_ticks,
        padding=args.padding,
        dt_col=args.dt_col,
        num_workers=args.num_workers,
        complib=args.complib,
        complevel=args.complevel,
    )


async def async_show(args):
    Data.show(args.input, args.index)


async def async_export(args):
    Data.export(args.input, args.output, args.chunk)
