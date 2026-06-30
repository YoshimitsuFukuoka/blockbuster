from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class MAConfig:
    short_period: int = 5
    long_period: int = 25


@dataclass
class RSIConfig:
    period: int = 14
    oversold: float = 30.0
    overbought: float = 70.0


@dataclass
class MACDConfig:
    fast: int = 12
    slow: int = 26
    signal: int = 9


@dataclass
class StrategyConfig:
    ma: MAConfig = field(default_factory=MAConfig)
    rsi: RSIConfig = field(default_factory=RSIConfig)
    macd: MACDConfig = field(default_factory=MACDConfig)
    combined_weights: dict[str, float] = field(
        default_factory=lambda: {"ma": 0.30, "rsi": 0.35, "macd": 0.35}
    )
    score_buy_threshold: float = 0.40
    score_sell_threshold: float = -0.40


@dataclass
class PortfolioConfig:
    initial_capital: float = 1_000_000.0
    max_position_pct: float = 0.10
    commission_rate: float = 0.001


@dataclass
class AWSConfig:
    region: str = "ap-northeast-1"
    s3_bucket: str = "blockbuster-reports"
    dynamodb_table: str = "blockbuster-portfolio"
    ses_sender: str = ""
    ses_recipient: str = ""


@dataclass
class AppConfig:
    tickers: list[str] = field(
        default_factory=lambda: ["7203.T", "6758.T", "9984.T", "6861.T", "8306.T"]
    )
    portfolio: PortfolioConfig = field(default_factory=PortfolioConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    backtest_start: str = "2022-01-01"
    backtest_end: str = "2024-12-31"
    aws: AWSConfig = field(default_factory=AWSConfig)


def _from_dict(cls: type, data: dict[str, Any]) -> Any:
    if not isinstance(data, dict):
        return data
    hints: dict[str, type] = {}
    import inspect
    for f in inspect.signature(cls).parameters.values():
        hints[f.name] = f.annotation
    kwargs: dict[str, Any] = {}
    for f_name, f_type in hints.items():
        if f_name not in data:
            continue
        val = data[f_name]
        origin = getattr(f_type, "__origin__", None)
        if isinstance(val, dict) and hasattr(f_type, "__dataclass_fields__"):
            kwargs[f_name] = _from_dict(f_type, val)
        else:
            kwargs[f_name] = val
    return cls(**kwargs)


def load_config(path: str | None = None) -> AppConfig:
    if path is None:
        path = os.environ.get(
            "CONFIG_PATH",
            os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml"),
        )
    with open(path, "r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    strategy_raw = raw.get("strategy", {})
    strategy = StrategyConfig(
        ma=_from_dict(MAConfig, strategy_raw.get("ma", {})),
        rsi=_from_dict(RSIConfig, strategy_raw.get("rsi", {})),
        macd=_from_dict(MACDConfig, strategy_raw.get("macd", {})),
        combined_weights=strategy_raw.get(
            "combined_weights", {"ma": 0.30, "rsi": 0.35, "macd": 0.35}
        ),
        score_buy_threshold=strategy_raw.get("score_buy_threshold", 0.40),
        score_sell_threshold=strategy_raw.get("score_sell_threshold", -0.40),
    )

    return AppConfig(
        tickers=raw.get("tickers", ["7203.T"]),
        portfolio=_from_dict(PortfolioConfig, raw.get("portfolio", {})),
        strategy=strategy,
        backtest_start=raw.get("backtest_start", "2022-01-01"),
        backtest_end=raw.get("backtest_end", "2024-12-31"),
        aws=_from_dict(AWSConfig, raw.get("aws", {})),
    )
