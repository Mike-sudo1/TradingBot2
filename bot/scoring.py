"""Fabio scoring and grading system."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class ScoreResult:
    symbol: str
    score: float
    grade: str
    details: Dict[str, float]


def fabio_score(symbol: str, *, trend: bool, macd_hist: float, rsi: float, vwap_prox: float, spread: float, volume: float) -> ScoreResult:
    """Compute composite score for Fabio strategy."""
    score = 0.0
    details = {}
    if trend:
        score += 1
        details["trend"] = 1
    else:
        details["trend"] = 0
    score += max(macd_hist, 0)
    details["macd"] = macd_hist
    score += max(0, 1 - abs(rsi - 50) / 50)
    details["rsi"] = rsi
    score += max(0, 1 - vwap_prox)
    details["vwap"] = vwap_prox
    score += max(0, 1 - spread)
    details["spread"] = spread
    score += volume
    details["volume"] = volume

    grade = "C"
    if score > 4:
        grade = "A"
    elif score > 3:
        grade = "B"

    return ScoreResult(symbol=symbol, score=score, grade=grade, details=details)


def format_fallback(result: ScoreResult, price: float, stop: float, qty_est: float, flags: str) -> str:
    return (
        f"dir=long grade={result.grade} px={price:.8f} stop={stop:.8f} "
        f"risk≈{abs(price-stop):.4f} qty_est≈{qty_est:.4f} {flags}"
    )


__all__ = ["ScoreResult", "fabio_score", "format_fallback"]
