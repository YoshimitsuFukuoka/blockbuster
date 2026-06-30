from __future__ import annotations

import logging
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

_TZ = "Asia/Tokyo"


class DataFetchError(Exception):
    pass


class DataFetcher:
    def fetch_historical(
        self,
        ticker: str,
        start: str,
        end: str,
        interval: str = "1d",
    ) -> pd.DataFrame:
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                interval=interval,
                auto_adjust=True,
                progress=False,
            )
        except Exception as exc:
            raise DataFetchError(f"Failed to fetch {ticker}: {exc}") from exc

        if df is None or df.empty:
            raise DataFetchError(f"No data returned for {ticker} ({start} to {end})")

        df = _normalize(df)
        logger.info("Fetched %d bars for %s (%s to %s)", len(df), ticker, start, end)
        return df

    def fetch_latest(self, ticker: str, lookback_days: int = 200) -> pd.DataFrame:
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=lookback_days * 2)).strftime(
            "%Y-%m-%d"
        )
        df = self.fetch_historical(ticker, start, end)
        return df.iloc[-lookback_days:] if len(df) > lookback_days else df

    def fetch_multiple(
        self,
        tickers: list[str],
        start: str,
        end: str,
    ) -> dict[str, pd.DataFrame]:
        result: dict[str, pd.DataFrame] = {}
        for ticker in tickers:
            try:
                result[ticker] = self.fetch_historical(ticker, start, end)
            except DataFetchError as exc:
                logger.warning("Skipping %s: %s", ticker, exc)
        return result


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index)
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert(_TZ)
    else:
        df.index = df.index.tz_convert(_TZ)
    df = df.dropna(subset=["Close"])
    df = df.sort_index()
    return df
