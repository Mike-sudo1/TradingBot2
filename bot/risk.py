"""Risk management helpers."""
from __future__ import annotations

import time
from dataclasses import dataclass

from .config import Config


@dataclass
class Position:
    symbol: str
    side: str
    entry_price: float
    stop: float
    take_profit: float
    qty: float


class RiskManager:
    def __init__(self, config: Config):
        self.config = config
        self.day_pnl = 0.0
        self.max_drawdown = 0.0
        self.cooldown_until = 0.0

    def update_pnl(self, pnl: float) -> None:
        self.day_pnl += pnl
        self.max_drawdown = min(self.max_drawdown, self.day_pnl)
        if self.day_pnl - self.max_drawdown <= -self.config.DAILY_MAX_DD_USDT:
            self.cooldown_until = float("inf")

    def can_trade(self) -> bool:
        return time.time() >= self.cooldown_until

    def start_cooldown(self) -> None:
        self.cooldown_until = time.time() + self.config.COOLDOWN_SEC

    def trailing_stop(self, position: Position, current_price: float) -> float:
        bps_gain = (current_price - position.entry_price) / position.entry_price * 10000
        if bps_gain > self.config.TRAIL_START_BPS:
            trail_price = current_price * (1 - self.config.TRAIL_STEP_BPS / 10000)
            position.stop = max(position.stop, trail_price)
        return position.stop


__all__ = ["Position", "RiskManager"]
