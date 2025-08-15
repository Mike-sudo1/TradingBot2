"""Technical indicators used by Fabio strategy."""
from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def ma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    rs = ema(up, period) / ema(down, period)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def vwap(df: pd.DataFrame) -> pd.Series:
    """Return rolling VWAP for intraday ticks."""
    pv = (df["price"] * df["volume"]).cumsum()
    vol = df["volume"].cumsum()
    return pv / vol


__all__ = ["ema", "ma", "rsi", "macd", "vwap"]
