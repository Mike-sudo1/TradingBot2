"""Fabio entry/exit logic."""
from __future__ import annotations

import pandas as pd
from typing import Dict, Optional

from .config import Config
from .indicators import ema, ma, rsi, macd, vwap
from .scoring import fabio_score, format_fallback, ScoreResult
from time import time

from .executor import (
    Executor,
    format_price,
    format_qty,
    size_position,
    notional_ok,
)
from .risk import Position, RiskManager
from .symbols import SymbolCache
from .logger import get_logger


class FabioStrategy:
    def __init__(self, config: Config, symbols: SymbolCache, executor: Executor, risk: RiskManager):
        self.config = config
        self.symbols = symbols
        self.executor = executor
        self.risk = risk
        self.logger = get_logger(config)
        self.data: Dict[str, pd.DataFrame] = {s: pd.DataFrame(columns=["price", "volume"]) for s in config.WATCHLIST}
        self.positions: Dict[str, Position] = {}
        self._decision_memo: Dict[str, tuple[float, str, float]] = {}

    def on_tick(self, symbol: str, bid: float, ask: float, volume: float = 0.0) -> Optional[Position]:
        mid = (bid + ask) / 2
        df = self.data[symbol]
        df.loc[pd.Timestamp.utcnow()] = {"price": mid, "volume": volume}
        if len(df) < 30:
            return None

        price_series = df["price"]
        rsi_val = rsi(price_series).iloc[-1]
        macd_line, signal_line, hist = macd(price_series)
        hist_val = hist.iloc[-1]
        trend = price_series.iloc[-1] > ma(price_series, 200).iloc[-1]
        vwap_val = vwap(df).iloc[-1]
        vwap_prox = abs(mid - vwap_val) / vwap_val
        spread = (ask - bid) / mid

        score = fabio_score(
            symbol,
            trend=trend,
            macd_hist=hist_val,
            rsi=rsi_val,
            vwap_prox=vwap_prox,
            spread=spread,
            volume=1.0,
        )

        if symbol in self.positions:
            pos = self.positions[symbol]
            # check exit conditions
            if mid <= pos.stop or mid >= pos.take_profit or hist_val < 0:
                pnl = (mid - pos.entry_price) * pos.qty - self.executor._calc_fee(mid * pos.qty)
                self.risk.update_pnl(pnl)
                self.logger.info(f"[SELL] {symbol} qty={pos.qty:.6f} px={mid:.2f} PnL={pnl:.2f}")
                del self.positions[symbol]
                self.risk.start_cooldown()
            else:
                self.risk.trailing_stop(pos, mid)
            return None

        grade_order = {"A": 3, "B": 2, "C": 1}
        if (
            grade_order.get(score.grade, 0) < grade_order.get(self.config.ENTRY_MIN_GRADE, 0)
            and score.score < self.config.ENTRY_MIN_SCORE
        ):
            self.logger.info(
                f"[SKIP] {symbol} reason=grade grade={score.grade} score={score.score:.2f}"
            )
            return None

        qty, reason = size_position(symbol, ask, self.config, self.symbols.filters)
        if qty == 0:
            notional = format_price(symbol, ask, self.symbols.filters) * format_qty(
                symbol, self.config.MAX_CAPITAL_USDT / ask, self.symbols.filters
            )
            threshold = self.config.MIN_NOTIONAL_USDT
            if reason == "min_qty":
                threshold = self.symbols.min_qty(symbol)
            self.logger.info(
                f"[SKIP] {symbol} reason={reason} px={ask:.2f} qty={notional/ask:.6f} "
                f"notional={notional:.2f} < {threshold:.2f}"
            )
            return None

        stop = mid * (1 - self.config.STOP_LOSS_BPS / 10000)
        tp = mid * (1 + self.config.PROFIT_TAKE_BPS / 10000)

        if not notional_ok(symbol, ask, qty, self.symbols.filters, self.config):
            mn = self.symbols.min_notional(symbol)
            notional = ask * qty
            self.logger.info(
                f"[SKIP] {symbol} reason=min_notional px={ask:.2f} qty={qty:.6f} notional={notional:.2f} < {mn:.2f}"
            )
            return None

        pos = Position(symbol, "LONG", mid, stop, tp, qty)
        self.positions[symbol] = pos
        result = self.executor.simulate(symbol, "BUY", qty, ask)
        self.logger.info(
            f"[BUY] {symbol} qty={qty:.6f} px={ask:.2f} notional={result.notional:.2f} fee={result.fee:.4f}"
        )

        risk_label = "risk_bps" if self.config.RISK_UNIT == "bps" else "risk_usdt"
        risk_val = (
            abs(mid - stop) / mid * 10_000
            if self.config.RISK_UNIT == "bps"
            else abs(mid - stop) * qty
        )

        if self.config.DEBUG and self._should_log(symbol, mid, score.grade):
            self.logger.debug(
                "[DECISION] "
                + format_fallback(score, mid, stop, qty, risk_label, risk_val, "")
            )
        return pos

    def _should_log(self, symbol: str, px: float, grade: str, every_ms: int = 200) -> bool:
        rounded = format_price(symbol, px, self.symbols.filters)
        last_px, last_grade, last_ts = self._decision_memo.get(symbol, (None, None, 0.0))
        now = time() * 1000
        if last_px == rounded and last_grade == grade and now - last_ts < every_ms:
            return False
        self._decision_memo[symbol] = (rounded, grade, now)
        return True


__all__ = ["FabioStrategy"]
