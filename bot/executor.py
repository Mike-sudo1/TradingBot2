"""Order execution and simulation layer.

This module provides utilities for respecting Binance precision filters
when sizing and sending orders.  Quantity/price rounding uses floor
quantisation so we never accidentally round *up* and violate filters.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Tuple

from binance.client import Client

from .config import Config
from .symbols import SymbolCache, SymbolFilters


@dataclass
class ExecutionResult:
    symbol: str
    side: str
    qty: float
    price: float
    notional: float
    fee: float
    executed: bool


def _quantize(value: float, step: float) -> float:
    """Floor the value to the given step using ``Decimal`` precision."""
    if step == 0:
        return value
    d_val = Decimal(str(value))
    d_step = Decimal(str(step))
    return float((d_val / d_step).to_integral_value(rounding=ROUND_DOWN) * d_step)


def format_qty(symbol: str, qty: float, filters: Dict[str, SymbolFilters]) -> float:
    return _quantize(qty, filters[symbol].step_size)


def format_price(symbol: str, px: float, filters: Dict[str, SymbolFilters]) -> float:
    return _quantize(px, filters[symbol].tick_size)


def min_qty(symbol: str, filters: Dict[str, SymbolFilters]) -> float:
    return filters[symbol].min_qty or 0.0


def min_notional(symbol: str, filters: Dict[str, SymbolFilters], cfg: Config) -> float:
    mn = filters[symbol].min_notional
    return mn if mn > 0 else cfg.MIN_NOTIONAL_USDT


def notional_ok(symbol: str, px: float, qty: float, filters: Dict[str, SymbolFilters], cfg: Config) -> bool:
    return px * qty >= min_notional(symbol, filters, cfg) - 1e-8


def size_position(symbol: str, px: float, cfg: Config, filters: Dict[str, SymbolFilters]) -> Tuple[float, str]:
    """Return (qty, reason). Qty=0 on failure with reason set."""
    step = filters[symbol].step_size
    mq = min_qty(symbol, filters)
    mn = min_notional(symbol, filters, cfg)

    qty = _quantize(cfg.MAX_CAPITAL_USDT / px, step)
    if qty < mq:
        qty = _quantize(mq, step)
        if qty < mq:
            return 0.0, "min_qty"

    if notional_ok(symbol, px, qty, filters, cfg):
        return qty, ""

    qty = _quantize(mn / px, step)
    if qty < mq or not notional_ok(symbol, px, qty, filters, cfg):
        return 0.0, "min_notional"
    return qty, ""


class Executor:
    def __init__(self, client: Client, symbols: SymbolCache, config: Config):
        self.client = client
        self.symbols = symbols
        self.config = config

    def _calc_fee(self, notional: float) -> float:
        return notional * self.config.FEE_TAKER

    def simulate(self, symbol: str, side: str, qty: float, price: float) -> ExecutionResult:
        price = format_price(symbol, price, self.symbols.filters)
        notional = qty * price
        fee = self._calc_fee(notional)
        return ExecutionResult(symbol, side, qty, price, notional, fee, executed=False)

    def market_order(self, symbol: str, side: str, qty: float) -> ExecutionResult:
        if not self.config.LIVE:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker["price"])
            return self.simulate(symbol, side, qty, price)

        order = self.client.create_order(symbol=symbol, side=side, type="MARKET", quantity=qty)
        fills = order.get("fills", [{}])
        price = float(fills[0].get("price", order.get("price", 0)))
        executed_qty = float(order.get("executedQty", qty))
        notional = executed_qty * price
        fee = sum(float(f["commission"]) for f in fills)
        return ExecutionResult(symbol, side, executed_qty, price, notional, fee, executed=True)


__all__ = [
    "Executor",
    "ExecutionResult",
    "format_price",
    "format_qty",
    "min_qty",
    "min_notional",
    "notional_ok",
    "size_position",
]

