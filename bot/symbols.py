"""Symbol utilities and exchange filter cache."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from binance.client import Client


@dataclass
class SymbolFilters:
    tick_size: float
    step_size: float
    min_qty: float
    min_notional: float


def _float(v: str) -> float:
    return float(v)


def fetch_symbol_filters(client: Client, symbols: list[str]) -> Dict[str, SymbolFilters]:
    """Fetch exchangeInfo and build filters for given symbols."""
    info = client.get_exchange_info()
    filters: Dict[str, SymbolFilters] = {}
    for s in info["symbols"]:
        symbol = s["symbol"]
        if symbol not in symbols:
            continue
        fs = {f["filterType"]: f for f in s["filters"]}
        lot = fs.get("LOT_SIZE")
        tick = fs.get("PRICE_FILTER")
        min_notional = fs.get("MIN_NOTIONAL")
        if not (lot and tick and min_notional):
            raise ValueError(f"Missing filters for {symbol}")
        filters[symbol] = SymbolFilters(
            tick_size=_float(tick["tickSize"]),
            step_size=_float(lot["stepSize"]),
            min_qty=_float(lot["minQty"]),
            min_notional=_float(min_notional.get("minNotional", "0")),
        )
    return filters


class SymbolCache:
    """Cache of symbol filters and precision helpers."""

    def __init__(self, filters: Dict[str, SymbolFilters]):
        self.filters = filters
        for sym, f in filters.items():
            print(
                f"[FILTERS] {sym} step={f.step_size:.8f} tick={f.tick_size:.8f} "
                f"minQty={f.min_qty:.8f} minNotional={f.min_notional:.2f}"
            )

    def step_size(self, symbol: str) -> float:
        return self.filters[symbol].step_size

    def tick_size(self, symbol: str) -> float:
        return self.filters[symbol].tick_size

    def min_qty(self, symbol: str) -> float:
        return self.filters[symbol].min_qty

    def min_notional(self, symbol: str) -> float:
        return self.filters[symbol].min_notional


__all__ = ["SymbolFilters", "fetch_symbol_filters", "SymbolCache"]
