"""Order execution and simulation layer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from binance.client import Client

from .config import Config
from .symbols import SymbolCache


@dataclass
class ExecutionResult:
    symbol: str
    side: str
    qty: float
    price: float
    notional: float
    fee: float
    executed: bool


class Executor:
    def __init__(self, client: Client, symbols: SymbolCache, config: Config):
        self.client = client
        self.symbols = symbols
        self.config = config

    def _calc_fee(self, notional: float) -> float:
        return notional * self.config.FEE_TAKER

    def simulate(self, symbol: str, side: str, qty: float, price: float) -> ExecutionResult:
        price = self.symbols.format_price(symbol, price)
        qty = self.symbols.format_qty(symbol, qty)
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


__all__ = ["Executor", "ExecutionResult"]
