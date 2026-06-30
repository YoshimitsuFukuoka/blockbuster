from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


def compute_ma(df: pd.DataFrame, short_period: int, long_period: int) -> pd.DataFrame:
    close = df["Close"]
    result = pd.DataFrame(index=df.index)
    result["ma_short"] = ema(close, short_period)
    result["ma_long"] = ema(close, long_period)
    diff = result["ma_short"] - result["ma_long"]
    prev_diff = diff.shift(1)
    result["golden_cross"] = (prev_diff < 0) & (diff >= 0)
    result["dead_cross"] = (prev_diff > 0) & (diff <= 0)
    return result
