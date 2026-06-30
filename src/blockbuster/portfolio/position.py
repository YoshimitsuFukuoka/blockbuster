from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Position:
    ticker: str
    shares: int
    avg_cost: float
    opened_at: str

    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_cost

    def unrealized_pnl(self, current_price: float) -> float:
        return self.shares * (current_price - self.avg_cost)

    def unrealized_pct(self, current_price: float) -> float:
        if self.avg_cost == 0:
            return 0.0
        return (current_price - self.avg_cost) / self.avg_cost

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "shares": self.shares,
            "avg_cost": self.avg_cost,
            "opened_at": self.opened_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        return cls(
            ticker=data["ticker"],
            shares=int(data["shares"]),
            avg_cost=float(data["avg_cost"]),
            opened_at=data["opened_at"],
        )
