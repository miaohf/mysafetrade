from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from safetrade.market import Candle


class Signal(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass(frozen=True)
class StrategyDecision:
    signal: Signal
    reason: str
    reference_price: float


class MovingAverageCrossStrategy:
    def __init__(self, short_window: int = 7, long_window: int = 25) -> None:
        if short_window <= 0 or long_window <= 0:
            raise ValueError("strategy windows must be positive")
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")

        self.short_window = short_window
        self.long_window = long_window

    def decide(self, candles: list[Candle]) -> StrategyDecision:
        if len(candles) < self.long_window + 1:
            return StrategyDecision(Signal.HOLD, "not enough candle data", candles[-1].close)

        closes = [candle.close for candle in candles]
        previous_short = _mean(closes[-self.short_window - 1 : -1])
        previous_long = _mean(closes[-self.long_window - 1 : -1])
        current_short = _mean(closes[-self.short_window :])
        current_long = _mean(closes[-self.long_window :])
        price = closes[-1]

        if previous_short <= previous_long and current_short > current_long:
            return StrategyDecision(Signal.BUY, "short MA crossed above long MA", price)

        if previous_short >= previous_long and current_short < current_long:
            return StrategyDecision(Signal.SELL, "short MA crossed below long MA", price)

        return StrategyDecision(
            Signal.HOLD,
            f"no cross: short={current_short:.4f}, long={current_long:.4f}",
            price,
        )


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)
