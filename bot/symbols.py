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
        lot = fs.get("LOT_SIZE", {})
        tick = fs.get("PRICE_FILTER", {})
        min_notional = fs.get("MIN_NOTIONAL", {}).get("minNotional", 0)
        filters[symbol] = SymbolFilters(
            tick_size=_float(tick.get("tickSize", "0.00000001")),
            step_size=_float(lot.get("stepSize", "0.00000001")),
            min_qty=_float(lot.get("minQty", "0.0")),
            min_notional=_float(min_notional or "0.0"),
        )
    return filters


class SymbolCache:
    """Cache of symbol filters and precision helpers."""

    def __init__(self, filters: Dict[str, SymbolFilters]):
        self.filters = filters

    def format_price(self, symbol: str, price: float) -> float:
        f = self.filters[symbol]
        step = f.tick_size
        return round(price / step) * step

    def format_qty(self, symbol: str, qty: float) -> float:
        f = self.filters[symbol]
        step = f.step_size
        return round(qty / step) * step

    def validate(self, symbol: str, qty: float, price: float) -> bool:
        f = self.filters[symbol]
        if qty < f.min_qty:
            return False
        if qty * price < f.min_notional:
            return False
        return True


__all__ = ["SymbolFilters", "fetch_symbol_filters", "SymbolCache"]
