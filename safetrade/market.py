from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen


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


def market_id_from_symbol(symbol: str) -> str:
    return symbol.replace("/", "").replace("-", "").replace("_", "").lower()


class SafeTradePublicMarketDataClient(MarketDataClient):
    def __init__(self, api_base_url: str, period: int = 60, timeout: float = 10.0) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._period = period
        self._timeout = timeout

    def get_recent_candles(self, symbol: str, limit: int = 60) -> list[Candle]:
        market_id = market_id_from_symbol(symbol)
        candles = self._fetch_klines(market_id, limit)
        ticker = self.get_ticker(market_id)
        last_price = float(ticker["last"])

        if candles:
            latest = candles[-1]
            candles[-1] = Candle(
                timestamp=datetime.now(timezone.utc).replace(microsecond=0),
                open=latest.open,
                high=max(latest.high, last_price),
                low=min(latest.low, last_price),
                close=last_price,
                volume=latest.volume,
            )
            return candles

        now = datetime.now(timezone.utc).replace(microsecond=0)
        return [Candle(now, last_price, last_price, last_price, last_price, 0.0)]

    def get_ticker(self, market_id: str) -> dict[str, Any]:
        return self._get_json(f"/trade/public/tickers/{market_id}")

    def _fetch_klines(self, market_id: str, limit: int) -> list[Candle]:
        query = urlencode({"period": self._period, "limit": limit})
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
        del symbol

        candles: list[Candle] = []
        price = self._start_price
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

        for index in range(limit):
            timestamp = now - timedelta(minutes=limit - index)
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
