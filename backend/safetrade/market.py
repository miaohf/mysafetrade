from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen


from safetrade.microstructure import MarketTrade, OrderBook, OrderBookLevel, parse_market_trade, parse_order_book


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketDataClient:
    def get_recent_candles(self, symbol: str, limit: int = 60) -> list[Candle]:
        raise NotImplementedError

    def get_klines(self, symbol: str, period: int, limit: int = 120) -> list[Candle]:
        raise NotImplementedError

    def get_order_book(self, symbol: str, limit: int = 10) -> OrderBook:
        raise NotImplementedError

    def get_recent_trades(self, symbol: str, limit: int = 20) -> list[MarketTrade]:
        raise NotImplementedError


def market_id_from_symbol(symbol: str) -> str:
    return symbol.replace("/", "").replace("-", "").replace("_", "").lower()


class SafeTradePublicMarketDataClient(MarketDataClient):
    def __init__(self, api_base_url: str, period: int = 60, timeout: float = 10.0) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._period = period
        self._timeout = timeout

    def get_recent_candles(self, symbol: str, limit: int = 60) -> list[Candle]:
        return self.get_klines(symbol, self._period, limit)

    def get_klines(self, symbol: str, period: int, limit: int = 120) -> list[Candle]:
        market_id = market_id_from_symbol(symbol)
        candles = self._fetch_klines(market_id, period, limit)
        ticker = self.get_ticker(market_id)
        last_price = float(ticker["last"])
        return _apply_last_price(candles, last_price)

    def get_ticker(self, market_id: str) -> dict[str, Any]:
        return self._get_json(f"/trade/public/tickers/{market_id}")

    def get_order_book(self, symbol: str, limit: int = 10) -> OrderBook:
        market_id = market_id_from_symbol(symbol)
        query = urlencode({"limit": limit})
        payload = self._get_json(f"/trade/public/markets/{market_id}/depth?{query}")
        if not isinstance(payload, dict):
            raise ValueError(f"unexpected depth response for {market_id}: {payload!r}")
        return parse_order_book(payload)

    def get_recent_trades(self, symbol: str, limit: int = 20) -> list[MarketTrade]:
        market_id = market_id_from_symbol(symbol)
        query = urlencode({"limit": limit})
        rows = self._get_json(f"/trade/public/markets/{market_id}/trades?{query}")
        if not isinstance(rows, list):
            raise ValueError(f"unexpected trades response for {market_id}: {rows!r}")
        return [parse_market_trade(row) for row in rows]

    def _fetch_klines(self, market_id: str, period: int, limit: int) -> list[Candle]:
        query = urlencode({"period": period, "limit": limit})
        rows = self._get_json(f"/trade/public/markets/{market_id}/k-line?{query}")

        if not isinstance(rows, list):
            raise ValueError(f"unexpected k-line response for {market_id}: {rows!r}")

        candles = [_parse_kline(row) for row in rows]
        candles.sort(key=lambda candle: candle.timestamp)
        return candles

    def _get_json(self, path: str) -> Any:
        request = Request(
            f"{self._api_base_url}{path}",
            headers={
                "Accept": "application/json",
                "User-Agent": "SafeTradeBot/0.1 (+https://safetrade.com)",
            },
        )
        with urlopen(request, timeout=self._timeout) as response:
            return json.loads(response.read().decode("utf-8"))


class MockMarketDataClient(MarketDataClient):
    """Deterministic enough for local dry-runs, but never for strategy validation."""

    def __init__(self, start_price: float = 100.0, volatility_pct: float = 0.03, seed: int = 42) -> None:
        self._start_price = start_price
        self._volatility_pct = volatility_pct
        self._random = random.Random(seed)

    def get_recent_candles(self, symbol: str, limit: int = 60) -> list[Candle]:
        return self.get_klines(symbol, 60, limit)

    def get_klines(self, symbol: str, period: int, limit: int = 120) -> list[Candle]:
        del symbol

        candles: list[Candle] = []
        price = self._start_price
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        step = timedelta(minutes=max(period, 1))

        for index in range(limit):
            timestamp = now - step * (limit - index - 1)
            open_price = price
            change_pct = self._random.uniform(-self._volatility_pct, self._volatility_pct)
            wick_pct = self._random.uniform(0, self._volatility_pct / 2)
            close_price = max(0.00000001, open_price * (1 + change_pct))
            high_price = max(open_price, close_price) * (1 + wick_pct)
            low_price = min(open_price, close_price) * (1 - wick_pct)
            volume = self._random.uniform(10, 100)

            candles.append(
                Candle(
                    timestamp=timestamp,
                    open=open_price,
                    high=high_price,
                    low=max(0.00000001, low_price),
                    close=close_price,
                    volume=volume,
                )
            )
            price = close_price

        return candles

    def get_order_book(self, symbol: str, limit: int = 10) -> OrderBook:
        del symbol
        price = self._start_price
        spread = price * 0.01
        asks = tuple(
            OrderBookLevel(price=price + spread * (index + 1), amount=self._random.uniform(100, 5000))
            for index in range(limit)
        )
        bids = tuple(
            OrderBookLevel(price=max(0.00000001, price - spread * (index + 1)), amount=self._random.uniform(100, 5000))
            for index in range(limit)
        )
        return OrderBook(asks=asks, bids=bids, sequence=self._random.randint(1, 999999))

    def get_recent_trades(self, symbol: str, limit: int = 20) -> list[MarketTrade]:
        del symbol
        now = datetime.now(timezone.utc).replace(microsecond=0)
        trades: list[MarketTrade] = []
        price = self._start_price
        for index in range(limit):
            side = "buy" if self._random.random() > 0.45 else "sell"
            amount = self._random.uniform(1, 200)
            total = price * amount
            trades.append(
                MarketTrade(
                    id=1_000_000 + index,
                    price=price,
                    amount=amount,
                    total=total,
                    side=side,
                    created_at=(now - timedelta(seconds=index * 7)).isoformat().replace("+00:00", "Z"),
                )
            )
        return trades


def _apply_last_price(candles: list[Candle], last_price: float) -> list[Candle]:
    if candles:
        latest = candles[-1]
        return [
            *candles[:-1],
            Candle(
                timestamp=datetime.now(timezone.utc).replace(microsecond=0),
                open=latest.open,
                high=max(latest.high, last_price),
                low=min(latest.low, last_price),
                close=last_price,
                volume=latest.volume,
            ),
        ]

    now = datetime.now(timezone.utc).replace(microsecond=0)
    return [Candle(now, last_price, last_price, last_price, last_price, 0.0)]


def candles_to_dict(candles: list[Candle]) -> list[dict[str, Any]]:
    return [
        {
            "timestamp": candle.timestamp.isoformat(),
            "open": candle.open,
            "high": candle.high,
            "low": candle.low,
            "close": candle.close,
            "volume": candle.volume,
        }
        for candle in candles
    ]


def _parse_kline(row: list[Any]) -> Candle:
    if len(row) < 6:
        raise ValueError(f"unexpected k-line row: {row!r}")

    timestamp, open_price, high_price, low_price, close_price, volume = row[:6]
    return Candle(
        timestamp=datetime.fromtimestamp(int(timestamp), tz=timezone.utc),
        open=float(open_price),
        high=float(high_price),
        low=float(low_price),
        close=float(close_price),
        volume=float(volume),
    )
