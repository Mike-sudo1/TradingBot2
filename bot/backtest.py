"""Lightweight backtester for Fabio strategy."""
from __future__ import annotations

import pandas as pd
from binance.client import Client

from .config import load_config
from .symbols import fetch_symbol_filters, SymbolCache
from .executor import Executor
from .risk import RiskManager
from .strategy import FabioStrategy
from .portfolio import Portfolio


def backtest(csv_path: str, symbol: str) -> dict:
    cfg = load_config()
    client = Client()
    filters = SymbolCache(fetch_symbol_filters(client, [symbol]))
    executor = Executor(client, filters, cfg)
    risk = RiskManager(cfg)
    strategy = FabioStrategy(cfg, filters, executor, risk)
    portfolio = Portfolio()

    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        pos = strategy.on_tick(symbol, row["bid"], row["ask"], row.get("volume", 0))
        # In backtest we may inspect positions after each tick
        if pos is None:
            continue

    return portfolio.summary()


if __name__ == "__main__":
    import sys

    csv_file = sys.argv[1]
    symbol = sys.argv[2]
    summary = backtest(csv_file, symbol)
    print(summary)


__all__ = ["backtest"]
