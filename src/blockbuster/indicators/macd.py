from __future__ import annotations

import pandas as pd

from blockbuster.indicators.moving_average import ema


def compute_macd(
    df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    close = df["Close"]
    ema_fast = ema(close, fast)
    ema_slow = ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line

    result = pd.DataFrame(index=df.index)
    result["macd_line"] = macd_line
    result["signal_line"] = signal_line
    result["macd_histogram"] = histogram
    return result
