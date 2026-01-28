from __future__ import annotations

import argparse
import asyncio
from pathlib import Path


def _cmd_harvest(args: argparse.Namespace) -> None:
    # keep imports local so CLI stays fast and unit-testable
    from harvester import DataHarvester

    import config

    basket_name = args.basket or config.TARGET_BASKET
    harvester = DataHarvester(basket_name=basket_name, exchange_id=args.exchange)
    try:
        asyncio.run(harvester.harvest())
    except KeyboardInterrupt:
        harvester.stop()


def _cmd_backtest(args: argparse.Namespace) -> None:
    if args.mode == "bulk":
        from backtesting.bulk_runner import main as bulk_main

        bulk_main()
        return

    from backtesting.backtest import run_backtest

    run_backtest()


def _cmd_candles_build(args: argparse.Namespace) -> None:
    from .candles import build_candles

    build_candles(args.inputs, interval=args.interval, output_path=args.output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="momontum")
    sub = parser.add_subparsers(dest="command", required=True)

    p_harvest = sub.add_parser("harvest", help="Run the market data harvester")
    p_harvest.add_argument("--exchange", default="binanceusdm", help="ccxt exchange id")
    p_harvest.add_argument("--basket", default=None, help="Asset basket name (see config.py)")
    p_harvest.set_defaults(func=_cmd_harvest)

    p_backtest = sub.add_parser("backtest", help="Run backtests")
    p_backtest.add_argument(
        "--mode",
        choices=["single", "bulk"],
        default="bulk",
        help="Backtest mode",
    )
    p_backtest.set_defaults(func=_cmd_backtest)

    p_candles = sub.add_parser("candles", help="Candle utilities")
    sub_candles = p_candles.add_subparsers(dest="candles_cmd", required=True)

    p_build = sub_candles.add_parser("build", help="Build OHLC candles from tick parquet")
    p_build.add_argument(
        "inputs",
        nargs="+",
        help="One or more tick parquet files OR a directory containing parquet files",
    )
    p_build.add_argument("--interval", default="1min", help="Candle interval, e.g. 1min, 5min, 1h")
    p_build.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output parquet path for candles",
    )
    p_build.set_defaults(func=_cmd_candles_build)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
