from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from safetrade.market import Candle
from safetrade.strategy import MovingAverageCrossStrategy


@dataclass(frozen=True)
class MovingAveragePoint:
    timestamp: str
    close: float
    ma7: float | None
    ma25: float | None


def moving_average(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            result.append(None)
            continue
        result.append(sum(values[index + 1 - window : index + 1]) / window)
    return result


def rsi(values: list[float], period: int = 14) -> list[float | None]:
    if len(values) <= period:
        return [None] * len(values)

    result: list[float | None] = [None] * period
    gains: list[float] = []
    losses: list[float] = []

    for index in range(1, period + 1):
        change = values[index] - values[index - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    for index in range(period, len(values)):
        if index > period:
            change = values[index] - values[index - 1]
            gain = max(change, 0.0)
            loss = max(-change, 0.0)
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100.0 - (100.0 / (1.0 + rs)))

    return result


def build_market_analysis(
    candles: list[Candle],
    ticker: dict[str, Any],
    strategy: MovingAverageCrossStrategy | None = None,
) -> dict[str, Any]:
    strategy = strategy or MovingAverageCrossStrategy()
    closes = [candle.close for candle in candles]
    ma7_series = moving_average(closes, strategy.short_window)
    ma25_series = moving_average(closes, strategy.long_window)
    rsi_series = rsi(closes)

    decision = strategy.decide(candles)
    latest_ma7 = ma7_series[-1]
    latest_ma25 = ma25_series[-1]
    latest_rsi = rsi_series[-1]

    points: list[dict[str, Any]] = []
    for candle, ma7, ma25, rsi_value in zip(candles, ma7_series, ma25_series, rsi_series, strict=True):
        points.append(
            {
                "timestamp": candle.timestamp.isoformat(),
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "ma7": ma7,
                "ma25": ma25,
                "rsi14": rsi_value,
            }
        )

    last_seven = closes[-strategy.short_window :]
    last_twenty_five = closes[-strategy.long_window :]

    return {
        "ticker": ticker,
        "strategy": {
            "short_window": strategy.short_window,
            "long_window": strategy.long_window,
            "signal": decision.signal.value,
            "reason": decision.reason,
            "reference_price": decision.reference_price,
        },
        "latest": {
            "price": closes[-1],
            "ma7": latest_ma7,
            "ma25": latest_ma25,
            "rsi14": latest_rsi,
            "ma7_above_ma25": latest_ma7 is not None and latest_ma25 is not None and latest_ma7 > latest_ma25,
        },
        "ma_calculation": {
            "short_window": strategy.short_window,
            "long_window": strategy.long_window,
            "short_closes": last_seven,
            "short_sum": sum(last_seven),
            "short_ma": latest_ma7,
            "long_closes": last_twenty_five,
            "long_sum": sum(last_twenty_five),
            "long_ma": latest_ma25,
            "formula_short": f"({' + '.join(f'{value:.4f}' for value in last_seven)}) / {strategy.short_window}",
            "formula_long": f"sum(last {strategy.long_window} closes) / {strategy.long_window}",
        },
        "points": points,
        "decision": {
            "signal": decision.signal.value,
            "reason": decision.reason,
            "reference_price": decision.reference_price,
        },
    }
