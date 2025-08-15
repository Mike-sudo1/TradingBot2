"""Portfolio accounting for the session."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import csv
from datetime import datetime, timezone

from .executor import ExecutionResult


@dataclass
class Trade:
    ts: datetime
    symbol: str
    side: str
    qty: float
    price: float
    fee: float
    pnl: float


@dataclass
class Portfolio:
    trades: List[Trade] = field(default_factory=list)

    def record(self, result: ExecutionResult, pnl: float = 0.0) -> None:
        self.trades.append(
            Trade(
                ts=datetime.now(timezone.utc),
                symbol=result.symbol,
                side=result.side,
                qty=result.qty,
                price=result.price,
                fee=result.fee,
                pnl=pnl,
            )
        )

    def summary(self) -> dict:
        realized = sum(t.pnl for t in self.trades)
        wins = sum(1 for t in self.trades if t.pnl > 0)
        losses = sum(1 for t in self.trades if t.pnl <= 0)
        return {
            "trades": len(self.trades),
            "realized": realized,
            "win_rate": wins / len(self.trades) if self.trades else 0,
            "wins": wins,
            "losses": losses,
        }

    def export_csv(self, path: str) -> None:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ts", "symbol", "side", "qty", "price", "fee", "pnl"])
            for t in self.trades:
                writer.writerow([t.ts.isoformat(), t.symbol, t.side, t.qty, t.price, t.fee, t.pnl])


__all__ = ["Portfolio", "Trade"]
