from __future__ import annotations

import pandas as pd

from blockbuster.config import StrategyConfig
from blockbuster.strategies.base import Signal, Strategy, StrategyResult
from blockbuster.strategies.ma_cross import MACrossStrategy
from blockbuster.strategies.macd_cross import MACDCrossStrategy
from blockbuster.strategies.rsi_contrarian import RSIContrarianStrategy


class CombinedStrategy(Strategy):
    def __init__(self, config: StrategyConfig) -> None:
        self.config = config
        self.sub_strategies: dict[str, Strategy] = {
            "ma": MACrossStrategy(config.ma),
            "rsi": RSIContrarianStrategy(config.rsi),
            "macd": MACDCrossStrategy(config.macd),
        }
        weights = config.combined_weights
        total = sum(weights.values())
        self.weights = {k: v / total for k, v in weights.items()}

    def generate(self, ticker: str, df: pd.DataFrame) -> StrategyResult:
        sub_results: dict[str, StrategyResult] = {}
        for name, strategy in self.sub_strategies.items():
            sub_results[name] = strategy.generate(ticker, df)

        combined_score = sum(
            self.weights.get(name, 0.0) * result.score
            for name, result in sub_results.items()
        )

        if combined_score >= self.config.score_buy_threshold:
            signal = Signal.BUY
        elif combined_score <= self.config.score_sell_threshold:
            signal = Signal.SELL
        else:
            signal = Signal.HOLD

        metadata = {"combined_score": round(combined_score, 4)}
        for name, result in sub_results.items():
            metadata[f"{name}_score"] = round(result.score, 4)
            metadata.update({f"{name}_{k}": v for k, v in result.metadata.items()})

        return StrategyResult(
            ticker=ticker,
            timestamp=df.index[-1],
            signal=signal,
            score=combined_score,
            metadata=metadata,
        )


def build_strategy(name: str, config: StrategyConfig) -> Strategy:
    if name == "ma":
        return MACrossStrategy(config.ma)
    if name == "rsi":
        return RSIContrarianStrategy(config.rsi)
    if name == "macd":
        return MACDCrossStrategy(config.macd)
    return CombinedStrategy(config)
