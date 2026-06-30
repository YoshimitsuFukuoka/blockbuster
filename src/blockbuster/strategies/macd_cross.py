from __future__ import annotations

import math

import pandas as pd

from blockbuster.config import MACDConfig
from blockbuster.indicators.macd import compute_macd
from blockbuster.strategies.base import Signal, Strategy, StrategyResult


class MACDCrossStrategy(Strategy):
    def __init__(self, config: MACDConfig) -> None:
        self.config = config

    def generate(self, ticker: str, df: pd.DataFrame) -> StrategyResult:
        ind = compute_macd(df, self.config.fast, self.config.slow, self.config.signal)
        if len(ind) < 2:
            return StrategyResult(ticker=ticker, timestamp=df.index[-1], signal=Signal.HOLD, score=0.0)

        curr = ind.iloc[-1]
        prev = ind.iloc[-2]
        ts = df.index[-1]

        curr_hist = float(curr["macd_histogram"])
        prev_hist = float(prev["macd_histogram"])

        if any(math.isnan(v) for v in [curr_hist, prev_hist]):
            return StrategyResult(ticker=ticker, timestamp=ts, signal=Signal.HOLD, score=0.0)

        bullish_cross = prev_hist < 0 and curr_hist >= 0
        bearish_cross = prev_hist > 0 and curr_hist <= 0

        # Scale score by histogram magnitude relative to recent range (cap at 1)
        hist_range = ind["macd_histogram"].abs().quantile(0.9)
        scale = min(abs(curr_hist) / hist_range, 1.0) if hist_range != 0 else 1.0

        if bullish_cross:
            score, signal = scale, Signal.BUY
        elif bearish_cross:
            score, signal = -scale, Signal.SELL
        else:
            score, signal = 0.0, Signal.HOLD

        return StrategyResult(
            ticker=ticker,
            timestamp=ts,
            signal=signal,
            score=score,
            metadata={
                "macd_line": round(float(curr["macd_line"]), 4),
                "signal_line": round(float(curr["signal_line"]), 4),
                "histogram": round(curr_hist, 4),
            },
        )
