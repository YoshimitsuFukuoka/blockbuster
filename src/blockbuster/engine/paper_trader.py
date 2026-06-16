from __future__ import annotations

import logging
from datetime import datetime

import pytz

from blockbuster.config import AppConfig
from blockbuster.data.fetcher import DataFetcher
from blockbuster.portfolio.portfolio import Portfolio, TradeRecord
from blockbuster.strategies.base import Signal, Strategy

logger = logging.getLogger(__name__)

_JST = pytz.timezone("Asia/Tokyo")
_TRADING_SESSIONS = [
    (9, 0, 11, 30),
    (12, 30, 15, 30),
]


def within_tse_trading_hours(now: datetime | None = None) -> bool:
    if now is None:
        now = datetime.now(_JST)
    elif now.tzinfo is None:
        now = _JST.localize(now)

    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    t = (now.hour, now.minute)
    for sh, sm, eh, em in _TRADING_SESSIONS:
        if (sh, sm) <= t <= (eh, em):
            return True
    return False


class PaperTrader:
    """Executes a single trading tick (designed for Lambda invocation)."""

    def __init__(
        self,
        config: AppConfig,
        strategy: Strategy,
        portfolio: Portfolio,
        fetcher: DataFetcher,
    ) -> None:
        self.config = config
        self.strategy = strategy
        self.portfolio = portfolio
        self.fetcher = fetcher

    def tick(self) -> list[TradeRecord]:
        """Fetch latest data, generate signals, execute virtual trades. Returns executed trades."""
        executed: list[TradeRecord] = []
        current_prices: dict[str, float] = {}

        # Determine lookback window
        warmup = max(
            self.config.strategy.ma.long_period,
            self.config.strategy.rsi.period + 1,
            self.config.strategy.macd.slow + self.config.strategy.macd.signal,
        )
        lookback = max(warmup * 3, 200)

        for ticker in self.config.tickers:
            try:
                df = self.fetcher.fetch_latest(ticker, lookback_days=lookback)
            except Exception as exc:
                logger.warning("Fetch failed for %s: %s", ticker, exc)
                continue

            if df.empty or len(df) < warmup:
                continue

            price = float(df["Close"].iloc[-1])
            current_prices[ticker] = price
            ts_str = str(df.index[-1])

            result = self.strategy.generate(ticker, df)
            logger.info(
                "Signal %s for %s (score=%.3f)",
                result.signal.name, ticker, result.score
            )

            if result.signal == Signal.BUY:
                trade = self.portfolio.buy(
                    ticker, price, ts_str,
                    self.config.portfolio.max_position_pct,
                    current_prices,
                )
                if trade:
                    executed.append(trade)
            elif result.signal == Signal.SELL:
                trade = self.portfolio.sell(ticker, price, ts_str)
                if trade:
                    executed.append(trade)

        return executed
