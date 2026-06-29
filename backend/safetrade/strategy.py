from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from safetrade.market import Candle
from safetrade.microstructure import MicrostructureMetrics

if TYPE_CHECKING:
    from safetrade.config import Settings


class Signal(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass(frozen=True)
class StrategyDecision:
    signal: Signal
    reason: str
    reference_price: float
    raw_signal: Signal
    rsi14: float | None
    volume: float
    average_volume: float | None
    volume_ratio: float | None
    quote_volume: float
    average_quote_volume: float | None


class MovingAverageCrossStrategy:
    def __init__(
        self,
        short_window: int = 7,
        long_window: int = 25,
        volume_window: int = 20,
        min_volume_ratio: float = 1.05,
        min_quote_volume: float = 50.0,
        max_buy_rsi: float = 75.0,
        max_spread_pct: float = 2.0,
        max_ask_bid_ratio: float = 1.5,
        min_buy_trade_ratio: float = 0.55,
    ) -> None:
        if short_window <= 0 or long_window <= 0:
            raise ValueError("strategy windows must be positive")
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")
        if volume_window <= 0:
            raise ValueError("volume_window must be positive")
        if min_volume_ratio < 0:
            raise ValueError("min_volume_ratio must not be negative")
        if min_quote_volume < 0:
            raise ValueError("min_quote_volume must not be negative")

        self.short_window = short_window
        self.long_window = long_window
        self.volume_window = volume_window
        self.min_volume_ratio = min_volume_ratio
        self.min_quote_volume = min_quote_volume
        self.max_buy_rsi = max_buy_rsi
        self.max_spread_pct = max_spread_pct
        self.max_ask_bid_ratio = max_ask_bid_ratio
        self.min_buy_trade_ratio = min_buy_trade_ratio

    def decide(
        self,
        candles: list[Candle],
        microstructure: MicrostructureMetrics | None = None,
    ) -> StrategyDecision:
        if len(candles) < self.long_window + 1:
            price = candles[-1].close
            return StrategyDecision(
                signal=Signal.HOLD,
                reason="not enough candle data",
                reference_price=price,
                raw_signal=Signal.HOLD,
                rsi14=None,
                volume=candles[-1].volume,
                average_volume=None,
                volume_ratio=None,
                quote_volume=candles[-1].volume * price,
                average_quote_volume=None,
            )

        closes = [candle.close for candle in candles]
        previous_short = _mean(closes[-self.short_window - 1 : -1])
        previous_long = _mean(closes[-self.long_window - 1 : -1])
        current_short = _mean(closes[-self.short_window :])
        current_long = _mean(closes[-self.long_window :])
        price = closes[-1]
        volume_snapshot = _volume_snapshot(candles, self.volume_window)
        current_rsi = _rsi_last(closes)

        if previous_short <= previous_long and current_short > current_long:
            if volume_snapshot.volume_ratio is None:
                return self._decision(Signal.HOLD, "buy blocked: not enough volume history", price, Signal.BUY, current_rsi, volume_snapshot)

            if volume_snapshot.volume_ratio < self.min_volume_ratio:
                return self._decision(
                    Signal.HOLD,
                    (
                        "buy blocked: MA cross lacks volume confirmation "
                        f"ratio={volume_snapshot.volume_ratio:.2f} < {self.min_volume_ratio:.2f}"
                    ),
                    price,
                    Signal.BUY,
                    current_rsi,
                    volume_snapshot,
                )

            if volume_snapshot.quote_volume < self.min_quote_volume:
                return self._decision(
                    Signal.HOLD,
                    (
                        "buy blocked: quote volume too low "
                        f"{volume_snapshot.quote_volume:.2f} < {self.min_quote_volume:.2f}"
                    ),
                    price,
                    Signal.BUY,
                    current_rsi,
                    volume_snapshot,
                )

            if current_rsi is not None and current_rsi >= self.max_buy_rsi:
                return self._decision(
                    Signal.HOLD,
                    f"buy blocked: RSI too hot {current_rsi:.2f} >= {self.max_buy_rsi:.2f}",
                    price,
                    Signal.BUY,
                    current_rsi,
                    volume_snapshot,
                )

            blocked_reason = _microstructure_buy_block(microstructure, self)
            if blocked_reason:
                return self._decision(
                    Signal.HOLD,
                    blocked_reason,
                    price,
                    Signal.BUY,
                    current_rsi,
                    volume_snapshot,
                )

            return self._decision(
                Signal.BUY,
                (
                    "short MA crossed above long MA with confirmation "
                    f"volume_ratio={volume_snapshot.volume_ratio:.2f} rsi={_fmt_optional(current_rsi)} "
                    f"spread={_fmt_optional(microstructure.spread_pct if microstructure else None)}% "
                    f"buy_ratio={_fmt_optional(microstructure.buy_quote_ratio if microstructure else None)}"
                ),
                price,
                Signal.BUY,
                current_rsi,
                volume_snapshot,
            )

        if previous_short >= previous_long and current_short < current_long:
            return self._decision(
                Signal.SELL,
                (
                    "short MA crossed below long MA "
                    f"volume_ratio={_fmt_optional(volume_snapshot.volume_ratio)} rsi={_fmt_optional(current_rsi)}"
                ),
                price,
                Signal.SELL,
                current_rsi,
                volume_snapshot,
            )

        return self._decision(
            Signal.HOLD,
            (
                f"no cross: short={current_short:.4f}, long={current_long:.4f}, "
                f"volume_ratio={_fmt_optional(volume_snapshot.volume_ratio)}, rsi={_fmt_optional(current_rsi)}, "
                f"spread={_fmt_optional(microstructure.spread_pct if microstructure else None)}%, "
                f"buy_ratio={_fmt_optional(microstructure.buy_quote_ratio if microstructure else None)}"
            ),
            price,
            Signal.HOLD,
            current_rsi,
            volume_snapshot,
        )

    def _decision(
        self,
        signal: Signal,
        reason: str,
        price: float,
        raw_signal: Signal,
        rsi14: float | None,
        volume_snapshot: "VolumeSnapshot",
    ) -> StrategyDecision:
        return StrategyDecision(
            signal=signal,
            reason=reason,
            reference_price=price,
            raw_signal=raw_signal,
            rsi14=rsi14,
            volume=volume_snapshot.volume,
            average_volume=volume_snapshot.average_volume,
            volume_ratio=volume_snapshot.volume_ratio,
            quote_volume=volume_snapshot.quote_volume,
            average_quote_volume=volume_snapshot.average_quote_volume,
        )


@dataclass(frozen=True)
class VolumeSnapshot:
    volume: float
    average_volume: float | None
    volume_ratio: float | None
    quote_volume: float
    average_quote_volume: float | None


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _volume_snapshot(candles: list[Candle], window: int) -> VolumeSnapshot:
    latest = candles[-1]
    quote_volume = latest.close * latest.volume
    previous = candles[-window - 1 : -1]
    if len(previous) < window:
        return VolumeSnapshot(
            volume=latest.volume,
            average_volume=None,
            volume_ratio=None,
            quote_volume=quote_volume,
            average_quote_volume=None,
        )

    average_volume = _mean([candle.volume for candle in previous])
    average_quote_volume = _mean([candle.close * candle.volume for candle in previous])
    volume_ratio = latest.volume / average_volume if average_volume > 0 else None
    return VolumeSnapshot(
        volume=latest.volume,
        average_volume=average_volume,
        volume_ratio=volume_ratio,
        quote_volume=quote_volume,
        average_quote_volume=average_quote_volume,
    )


def _rsi_last(values: list[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None

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
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _fmt_optional(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.2f}"


def _microstructure_buy_block(
    microstructure: MicrostructureMetrics | None,
    strategy: MovingAverageCrossStrategy,
) -> str | None:
    if microstructure is None:
        return "buy blocked: microstructure data unavailable"

    if microstructure.spread_pct is None:
        return "buy blocked: order book spread unavailable"

    if microstructure.spread_pct > strategy.max_spread_pct:
        return (
            "buy blocked: spread too wide "
            f"{microstructure.spread_pct:.2f}% > {strategy.max_spread_pct:.2f}%"
        )

    if microstructure.ask_bid_ratio is None:
        return "buy blocked: order book depth unavailable"

    if microstructure.ask_bid_ratio > strategy.max_ask_bid_ratio:
        return (
            "buy blocked: ask-side depth too heavy "
            f"ratio={microstructure.ask_bid_ratio:.2f} > {strategy.max_ask_bid_ratio:.2f}"
        )

    if microstructure.buy_quote_ratio is None:
        return "buy blocked: recent trades unavailable"

    if microstructure.buy_quote_ratio < strategy.min_buy_trade_ratio:
        return (
            "buy blocked: recent trades lack buy pressure "
            f"ratio={microstructure.buy_quote_ratio:.2f} < {strategy.min_buy_trade_ratio:.2f}"
        )

    return None


def build_strategy(settings: Settings) -> MovingAverageCrossStrategy:
    return MovingAverageCrossStrategy(
        volume_window=settings.strategy_volume_window,
        min_volume_ratio=settings.strategy_min_volume_ratio,
        min_quote_volume=settings.strategy_min_quote_volume,
        max_buy_rsi=settings.strategy_max_buy_rsi,
        max_spread_pct=settings.strategy_max_spread_pct,
        max_ask_bid_ratio=settings.strategy_max_ask_bid_ratio,
        min_buy_trade_ratio=settings.strategy_min_buy_trade_ratio,
    )
