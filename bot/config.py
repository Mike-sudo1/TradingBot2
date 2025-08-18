"""Configuration loader for trading bot."""
from __future__ import annotations

from dataclasses import dataclass, field
from dotenv import load_dotenv
import os
from typing import List


@dataclass
class Config:
    """Runtime configuration loaded from environment variables."""

    # API keys
    BINANCE_API_KEY: str | None = None
    BINANCE_API_SECRET: str | None = None

    # Execution / behaviour flags
    LIVE: bool = False
    DEBUG: bool = False
    DRY_LOG_TRADES_ONLY: bool = False

    WATCHLIST: List[str] = field(default_factory=lambda: ["BTCUSDT"])

    MAX_CAPITAL_USDT: float = 25.0
    DAILY_MAX_DD_USDT: float = 2.0
    FEE_TAKER: float = 0.001

    PROFIT_TAKE_BPS: float = 30.0
    STOP_LOSS_BPS: float = 20.0
    TRAIL_START_BPS: float = 15.0
    TRAIL_STEP_BPS: float = 5.0

    MIN_SPREAD_BPS: float = 1.0
    MIN_NOTIONAL_USDT: float = 5.0
    COOLDOWN_SEC: int = 15
    MAX_OPEN_TRADES: int = 1
    SLIPPAGE_BPS: float = 2.0

    ENTRY_MIN_GRADE: str = "B"
    ENTRY_MIN_SCORE: float = 0.0
    RISK_UNIT: str = "bps"  # 'bps' or 'usdt'

    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None


def _bool(env: os._Environ[str], key: str, default: bool) -> bool:
    return env.get(key, str(default)).lower() in {"1", "true", "yes", "on"}


def _float(env: os._Environ[str], key: str, default: float) -> float:
    try:
        return float(env.get(key, default))
    except ValueError:
        return float(default)


def load_config() -> Config:
    """Load configuration from environment variables."""
    load_dotenv()
    env = os.environ

    watchlist = env.get("WATCHLIST", "BTCUSDT")
    symbols = [s.strip().upper() for s in watchlist.split(",") if s.strip()]

    return Config(
        BINANCE_API_KEY=env.get("BINANCE_API_KEY"),
        BINANCE_API_SECRET=env.get("BINANCE_API_SECRET"),
        LIVE=_bool(env, "LIVE", False),
        DEBUG=_bool(env, "DEBUG", False),
        DRY_LOG_TRADES_ONLY=_bool(env, "DRY_LOG_TRADES_ONLY", False),
        WATCHLIST=symbols,
        MAX_CAPITAL_USDT=_float(env, "MAX_CAPITAL_USDT", 25.0),
        DAILY_MAX_DD_USDT=_float(env, "DAILY_MAX_DD_USDT", 2.0),
        FEE_TAKER=_float(env, "FEE_TAKER", 0.001),
        PROFIT_TAKE_BPS=_float(env, "PROFIT_TAKE_BPS", 30.0),
        STOP_LOSS_BPS=_float(env, "STOP_LOSS_BPS", 20.0),
        TRAIL_START_BPS=_float(env, "TRAIL_START_BPS", 15.0),
        TRAIL_STEP_BPS=_float(env, "TRAIL_STEP_BPS", 5.0),
        MIN_SPREAD_BPS=_float(env, "MIN_SPREAD_BPS", 1.0),
        MIN_NOTIONAL_USDT=_float(env, "MIN_NOTIONAL_USDT", 5.0),
        COOLDOWN_SEC=int(env.get("COOLDOWN_SEC", 15)),
        MAX_OPEN_TRADES=int(env.get("MAX_OPEN_TRADES", 1)),
        SLIPPAGE_BPS=_float(env, "SLIPPAGE_BPS", 2.0),
        TELEGRAM_BOT_TOKEN=env.get("TELEGRAM_BOT_TOKEN"),
        TELEGRAM_CHAT_ID=env.get("TELEGRAM_CHAT_ID"),
        ENTRY_MIN_GRADE=env.get("ENTRY_MIN_GRADE", "B").upper(),
        ENTRY_MIN_SCORE=_float(env, "ENTRY_MIN_SCORE", 0.0),
        RISK_UNIT=env.get("RISK_UNIT", "bps").lower(),
    )


__all__ = ["Config", "load_config"]
