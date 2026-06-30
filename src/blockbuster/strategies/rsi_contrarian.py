from __future__ import annotations

import math

import pandas as pd

from blockbuster.config import RSIConfig
from blockbuster.indicators.rsi import compute_rsi
from blockbuster.strategies.base import Signal, Strategy, StrategyResult


class RSIContrarianStrategy(Strategy):
    def __init__(self, config: RSIConfig) -> None:
        self.config = config

    def generate(self, ticker: str, df: pd.DataFrame) -> StrategyResult:
        ind = compute_rsi(df, self.config.period)
        rsi_val = float(ind["rsi"].iloc[-1])
        ts = df.index[-1]

        if math.isnan(rsi_val):
            return StrategyResult(ticker=ticker, timestamp=ts, signal=Signal.HOLD, score=0.0)

        if rsi_val < self.config.oversold:
            score = (self.config.oversold - rsi_val) / self.config.oversold
            score = min(score, 1.0)
            signal = Signal.BUY
        elif rsi_val > self.config.overbought:
            score = -((rsi_val - self.config.overbought) / (100.0 - self.config.overbought))
            score = max(score, -1.0)
            signal = Signal.SELL
        else:
            score, signal = 0.0, Signal.HOLD

        return StrategyResult(
            ticker=ticker,
            timestamp=ts,
            signal=signal,
            score=score,
            metadata={"rsi": round(rsi_val, 2)},
        )
