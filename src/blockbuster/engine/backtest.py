from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from blockbuster.config import AppConfig
from blockbuster.data.fetcher import DataFetcher
from blockbuster.portfolio.portfolio import Portfolio, TradeRecord
from blockbuster.strategies.base import Signal, Strategy

logger = logging.getLogger(__name__)


@dataclass
class BacktestResult:
    trades: list[TradeRecord]
    equity_curve: pd.Series
    signals: list[dict]


class BacktestEngine:
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

    def run(self) -> BacktestResult:
        logger.info(
            "Starting backtest %s to %s", self.config.backtest_start, self.config.backtest_end
        )
        data = self.fetcher.fetch_multiple(
            self.config.tickers, self.config.backtest_start, self.config.backtest_end
        )
        if not data:
            raise RuntimeError("No data fetched for any ticker")

        # Align dates: use union of all available dates
        all_dates = sorted(
            set().union(*[set(df.index) for df in data.values()])
        )

        warmup = self._warmup_bars()
        equity_curve: dict[pd.Timestamp, float] = {}
        signals_log: list[dict] = []

        for i, date in enumerate(all_dates[warmup:], start=warmup):
            current_prices: dict[str, float] = {}
            for ticker, df in data.items():
                bars_up_to_now = df[df.index <= date]
                if bars_up_to_now.empty:
                    continue
                current_prices[ticker] = float(bars_up_to_now["Close"].iloc[-1])

            # Generate signals and execute
            for ticker, df in data.items():
                bars = df[df.index <= date]
                if len(bars) < warmup:
                    continue
                price = current_prices.get(ticker)
                if price is None:
                    continue

                result = self.strategy.generate(ticker, bars)
                ts_str = str(date)
                signals_log.append({"date": ts_str, "ticker": ticker, **result.metadata, "signal": result.signal.name, "score": round(result.score, 4)})

                if result.signal == Signal.BUY:
                    self.portfolio.buy(
                        ticker, price, ts_str,
                        self.config.portfolio.max_position_pct,
                        current_prices,
                    )
                elif result.signal == Signal.SELL:
                    self.portfolio.sell(ticker, price, ts_str)

            equity_curve[date] = self.portfolio.portfolio_value(current_prices)

        # Close all open positions at last available price
        final_prices: dict[str, float] = {}
        for ticker, df in data.items():
            if not df.empty:
                final_prices[ticker] = float(df["Close"].iloc[-1])
        last_date_str = str(all_dates[-1]) if all_dates else ""
        for ticker in list(self.portfolio.positions.keys()):
            price = final_prices.get(ticker)
            if price:
                self.portfolio.sell(ticker, price, last_date_str)

        equity_series = pd.Series(equity_curve)
        logger.info("Backtest complete: %d trades", len(self.portfolio.trade_history))
        return BacktestResult(
            trades=self.portfolio.trade_history,
            equity_curve=equity_series,
            signals=signals_log,
        )

    def _warmup_bars(self) -> int:
        sc = self.config.strategy
        return max(
            sc.ma.long_period,
            sc.rsi.period + 1,
            sc.macd.slow + sc.macd.signal,
        )
