from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

import pandas as pd


class Signal(IntEnum):
    SELL = -1
    HOLD = 0
    BUY = 1


@dataclass
class StrategyResult:
    ticker: str
    timestamp: pd.Timestamp
    signal: Signal
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class Strategy(ABC):
    @abstractmethod
    def generate(self, ticker: str, df: pd.DataFrame) -> StrategyResult:
        """Generate a signal from df, treating the last row as the current bar."""
        ...
