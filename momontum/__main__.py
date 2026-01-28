import argparse
import asyncio


def _cmd_harvest(args: argparse.Namespace) -> None:
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

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
