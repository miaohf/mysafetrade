from __future__ import annotations

from typing import Any

from safetrade.market import Candle, MarketDataClient
from safetrade.microstructure import (
    analyze_microstructure,
    microstructure_to_dict,
    order_book_to_dict,
    trades_to_dict,
)
from safetrade.strategy import MovingAverageCrossStrategy, build_strategy
from safetrade.config import Settings


def moving_average(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            result.append(None)
            continue
        result.append(sum(values[index + 1 - window : index + 1]) / window)
    return result


def previous_moving_average(values: list[float], window: int) -> list[float | None]:
    result: list[float | None] = []
    for index in range(len(values)):
        if index < window:
            result.append(None)
            continue
        result.append(sum(values[index - window : index]) / window)
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
    market: MarketDataClient,
    settings: Settings,
    strategy: MovingAverageCrossStrategy | None = None,
) -> dict[str, Any]:
    strategy = strategy or build_strategy(settings)
    order_book = market.get_order_book(settings.symbol, limit=settings.order_book_limit)
    recent_trades = market.get_recent_trades(settings.symbol, limit=settings.recent_trades_limit)
    microstructure = analyze_microstructure(order_book, recent_trades)

    closes = [candle.close for candle in candles]
    volumes = [candle.volume for candle in candles]
    quote_volumes = [candle.close * candle.volume for candle in candles]
    ma7_series = moving_average(closes, strategy.short_window)
    ma25_series = moving_average(closes, strategy.long_window)
    volume_ma_series = previous_moving_average(volumes, strategy.volume_window)
    quote_volume_ma_series = previous_moving_average(quote_volumes, strategy.volume_window)
    rsi_series = rsi(closes)

    decision = strategy.decide(candles, microstructure)
    latest_ma7 = ma7_series[-1]
    latest_ma25 = ma25_series[-1]
    latest_rsi = rsi_series[-1]
    latest_volume = volumes[-1]
    latest_quote_volume = quote_volumes[-1]
    latest_average_volume = volume_ma_series[-1]
    latest_volume_ratio = (
        latest_volume / latest_average_volume
        if latest_average_volume is not None and latest_average_volume > 0
        else None
    )

    points: list[dict[str, Any]] = []
    for candle, ma7, ma25, volume_ma, quote_volume_ma, rsi_value in zip(
        candles,
        ma7_series,
        ma25_series,
        volume_ma_series,
        quote_volume_ma_series,
        rsi_series,
        strict=True,
    ):
        points.append(
            {
                "timestamp": candle.timestamp.isoformat(),
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
                "quote_volume": candle.close * candle.volume,
                "volume_ma": volume_ma,
                "quote_volume_ma": quote_volume_ma,
                "ma7": ma7,
                "ma25": ma25,
                "rsi14": rsi_value,
            }
        )

    last_seven = closes[-strategy.short_window :]
    last_twenty_five = closes[-strategy.long_window :]
    micro_dict = microstructure_to_dict(microstructure)

    return {
        "ticker": ticker,
        "order_book": order_book_to_dict(order_book, limit=settings.order_book_limit),
        "recent_trades": trades_to_dict(recent_trades, limit=settings.recent_trades_limit),
        "microstructure": micro_dict,
        "strategy": {
            "short_window": strategy.short_window,
            "long_window": strategy.long_window,
            "volume_window": strategy.volume_window,
            "min_volume_ratio": strategy.min_volume_ratio,
            "min_quote_volume": strategy.min_quote_volume,
            "max_buy_rsi": strategy.max_buy_rsi,
            "max_spread_pct": strategy.max_spread_pct,
            "max_ask_bid_ratio": strategy.max_ask_bid_ratio,
            "min_buy_trade_ratio": strategy.min_buy_trade_ratio,
            "signal": decision.signal.value,
            "raw_signal": decision.raw_signal.value,
            "reason": decision.reason,
            "reference_price": decision.reference_price,
        },
        "latest": {
            "price": closes[-1],
            "ma7": latest_ma7,
            "ma25": latest_ma25,
            "rsi14": latest_rsi,
            "volume": latest_volume,
            "volume_ma": latest_average_volume,
            "volume_ratio": latest_volume_ratio,
            "quote_volume": latest_quote_volume,
            "quote_volume_ma": quote_volume_ma_series[-1],
            "ma7_above_ma25": latest_ma7 is not None and latest_ma25 is not None and latest_ma7 > latest_ma25,
            "spread_pct": microstructure.spread_pct,
            "ask_bid_ratio": microstructure.ask_bid_ratio,
            "buy_quote_ratio": microstructure.buy_quote_ratio,
        },
        "volume_analysis": {
            "window": strategy.volume_window,
            "latest_volume": latest_volume,
            "average_volume": latest_average_volume,
            "volume_ratio": latest_volume_ratio,
            "latest_quote_volume": latest_quote_volume,
            "average_quote_volume": quote_volume_ma_series[-1],
            "min_volume_ratio": strategy.min_volume_ratio,
            "min_quote_volume": strategy.min_quote_volume,
            "volume_confirmed": latest_volume_ratio is not None and latest_volume_ratio >= strategy.min_volume_ratio,
            "quote_volume_confirmed": latest_quote_volume >= strategy.min_quote_volume,
        },
        "microstructure_analysis": {
            **micro_dict,
            "max_spread_pct": strategy.max_spread_pct,
            "max_ask_bid_ratio": strategy.max_ask_bid_ratio,
            "min_buy_trade_ratio": strategy.min_buy_trade_ratio,
            "spread_confirmed": microstructure.spread_pct is not None and microstructure.spread_pct <= strategy.max_spread_pct,
            "depth_confirmed": microstructure.ask_bid_ratio is not None and microstructure.ask_bid_ratio <= strategy.max_ask_bid_ratio,
            "buy_pressure_confirmed": microstructure.buy_quote_ratio is not None and microstructure.buy_quote_ratio >= strategy.min_buy_trade_ratio,
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
            "raw_signal": decision.raw_signal.value,
            "reason": decision.reason,
            "reference_price": decision.reference_price,
        },
    }
