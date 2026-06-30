from __future__ import annotations

import pandas as pd

from blockbuster.config import MAConfig
from blockbuster.indicators.moving_average import compute_ma
from blockbuster.strategies.base import Signal, Strategy, StrategyResult


class MACrossStrategy(Strategy):
    def __init__(self, config: MAConfig) -> None:
        self.config = config

    def generate(self, ticker: str, df: pd.DataFrame) -> StrategyResult:
        ind = compute_ma(df, self.config.short_period, self.config.long_period)
        last = ind.iloc[-1]
        ts = df.index[-1]

        if last["golden_cross"]:
            score, signal = 1.0, Signal.BUY
        elif last["dead_cross"]:
            score, signal = -1.0, Signal.SELL
        else:
            score, signal = 0.0, Signal.HOLD

        return StrategyResult(
            ticker=ticker,
            timestamp=ts,
            signal=signal,
            score=score,
            metadata={
                "ma_short": round(float(last["ma_short"]), 2),
                "ma_long": round(float(last["ma_long"]), 2),
            },
        )
