"""CLI entry point for the trading bot."""
from __future__ import annotations

import argparse
import asyncio
import signal

from binance.client import Client

from .config import load_config, Config
from .symbols import fetch_symbol_filters, SymbolCache
from .executor import Executor
from .risk import RiskManager
from .strategy import FabioStrategy
from .streams import subscribe_book_ticker


async def run(cfg: Config) -> None:
    client = Client(cfg.BINANCE_API_KEY, cfg.BINANCE_API_SECRET)
    filters = SymbolCache(fetch_symbol_filters(client, cfg.WATCHLIST))
    executor = Executor(client, filters, cfg)
    risk = RiskManager(cfg)
    strategy = FabioStrategy(cfg, filters, executor, risk)

    async def consumer():
        async for msg in subscribe_book_ticker(cfg.WATCHLIST):
            data = msg.get("data", {})
            symbol = data.get("s")
            bid = float(data.get("b", 0))
            ask = float(data.get("a", 0))
            strategy.on_tick(symbol, bid, ask)

    task = asyncio.create_task(consumer())

    stop_event = asyncio.Event()

    def _stop(*_: object) -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_running_loop().add_signal_handler(sig, _stop)

    await stop_event.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--live", type=str, default=None)
    p.add_argument("--debug", type=str, default=None)
    p.add_argument("--trades-only", type=str, default=None)
    p.add_argument("--watchlist", type=str, default=None)
    return p.parse_args()


def apply_overrides(cfg: Config, args: argparse.Namespace) -> Config:
    if args.live is not None:
        cfg.LIVE = args.live.lower() in {"1", "true", "yes", "on"}
    if args.debug is not None:
        cfg.DEBUG = args.debug.lower() in {"1", "true", "yes", "on"}
    if args.trades_only is not None:
        cfg.DRY_LOG_TRADES_ONLY = args.trades_only.lower() in {"1", "true", "yes", "on"}
    if args.watchlist:
        cfg.WATCHLIST = [s.strip().upper() for s in args.watchlist.split(",") if s.strip()]
    return cfg


def main() -> None:
    cfg = load_config()
    args = parse_args()
    cfg = apply_overrides(cfg, args)
    asyncio.run(run(cfg))


if __name__ == "__main__":
    main()
