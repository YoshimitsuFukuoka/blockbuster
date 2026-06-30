from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from blockbuster.portfolio.position import Position

logger = logging.getLogger(__name__)

_LOT_SIZE = 100  # TSE standard round lot (単元株)


@dataclass
class TradeRecord:
    timestamp: str
    ticker: str
    action: str  # "BUY" | "SELL"
    shares: int
    price: float
    commission: float
    pnl: float | None = None  # realized P&L on SELL

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "ticker": self.ticker,
            "action": self.action,
            "shares": self.shares,
            "price": self.price,
            "commission": self.commission,
            "pnl": self.pnl,
        }


class Portfolio:
    def __init__(self, initial_capital: float, commission_rate: float) -> None:
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.positions: dict[str, Position] = {}
        self.trade_history: list[TradeRecord] = []

    def buy(
        self,
        ticker: str,
        price: float,
        timestamp: str,
        max_position_pct: float,
        current_prices: dict[str, float] | None = None,
    ) -> TradeRecord | None:
        if ticker in self.positions:
            return None  # Already holding

        portfolio_val = self.portfolio_value(current_prices or {ticker: price})
        budget = min(portfolio_val * max_position_pct, self.cash)
        gross_shares = int(budget / price)
        shares = (gross_shares // _LOT_SIZE) * _LOT_SIZE
        if shares <= 0:
            logger.debug("Insufficient funds to buy %s at %.2f", ticker, price)
            return None

        cost = shares * price
        commission = cost * self.commission_rate
        total_cost = cost + commission

        if total_cost > self.cash:
            shares = (int((self.cash / (price * (1 + self.commission_rate))) // _LOT_SIZE)) * _LOT_SIZE
            if shares <= 0:
                return None
            cost = shares * price
            commission = cost * self.commission_rate
            total_cost = cost + commission

        self.cash -= total_cost
        self.positions[ticker] = Position(
            ticker=ticker, shares=shares, avg_cost=price, opened_at=timestamp
        )
        record = TradeRecord(
            timestamp=timestamp,
            ticker=ticker,
            action="BUY",
            shares=shares,
            price=price,
            commission=commission,
        )
        self.trade_history.append(record)
        logger.info("BUY %s: %d shares @ %.2f (commission %.2f)", ticker, shares, price, commission)
        return record

    def sell(
        self,
        ticker: str,
        price: float,
        timestamp: str,
    ) -> TradeRecord | None:
        position = self.positions.pop(ticker, None)
        if position is None:
            return None

        proceeds = position.shares * price
        commission = proceeds * self.commission_rate
        net_proceeds = proceeds - commission
        pnl = net_proceeds - position.cost_basis

        self.cash += net_proceeds
        record = TradeRecord(
            timestamp=timestamp,
            ticker=ticker,
            action="SELL",
            shares=position.shares,
            price=price,
            commission=commission,
            pnl=pnl,
        )
        self.trade_history.append(record)
        logger.info("SELL %s: %d shares @ %.2f PnL=%.2f", ticker, position.shares, price, pnl)
        return record

    def portfolio_value(self, current_prices: dict[str, float]) -> float:
        position_value = sum(
            pos.shares * current_prices.get(ticker, pos.avg_cost)
            for ticker, pos in self.positions.items()
        )
        return self.cash + position_value

    def snapshot(self, current_prices: dict[str, float]) -> dict[str, Any]:
        total = self.portfolio_value(current_prices)
        return {
            "cash": round(self.cash, 2),
            "total_value": round(total, 2),
            "return_pct": round((total - self.initial_capital) / self.initial_capital * 100, 2),
            "positions": {
                ticker: {
                    "shares": pos.shares,
                    "avg_cost": pos.avg_cost,
                    "current_price": current_prices.get(ticker, pos.avg_cost),
                    "unrealized_pnl": round(pos.unrealized_pnl(current_prices.get(ticker, pos.avg_cost)), 2),
                }
                for ticker, pos in self.positions.items()
            },
        }

    def to_state(self) -> dict[str, Any]:
        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "commission_rate": self.commission_rate,
            "positions": {t: p.to_dict() for t, p in self.positions.items()},
            "trade_history": [r.to_dict() for r in self.trade_history[-100:]],
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> "Portfolio":
        p = cls(
            initial_capital=float(state["initial_capital"]),
            commission_rate=float(state["commission_rate"]),
        )
        p.cash = float(state["cash"])
        p.positions = {
            t: Position.from_dict(d) for t, d in state.get("positions", {}).items()
        }
        p.trade_history = [
            TradeRecord(**r) for r in state.get("trade_history", [])
        ]
        return p
