from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OrderBookLevel:
    price: float
    amount: float

    @property
    def quote(self) -> float:
        return self.price * self.amount


@dataclass(frozen=True)
class OrderBook:
    asks: tuple[OrderBookLevel, ...]
    bids: tuple[OrderBookLevel, ...]
    sequence: int | None = None


@dataclass(frozen=True)
class MarketTrade:
    id: int
    price: float
    amount: float
    total: float
    side: str
    created_at: str


@dataclass(frozen=True)
class MicrostructureMetrics:
    best_bid: float | None
    best_ask: float | None
    spread_pct: float | None
    bid_quote_total: float
    ask_quote_total: float
    ask_bid_ratio: float | None
    recent_trade_count: int
    buy_trade_ratio: float | None
    buy_quote_ratio: float | None


def parse_order_book(payload: dict[str, Any]) -> OrderBook:
    asks = tuple(_parse_level(row) for row in payload.get("asks", []))
    bids = tuple(_parse_level(row) for row in payload.get("bids", []))
    sequence = payload.get("sequence")
    return OrderBook(
        asks=asks,
        bids=bids,
        sequence=int(sequence) if sequence is not None else None,
    )


def parse_market_trade(row: dict[str, Any]) -> MarketTrade:
    return MarketTrade(
        id=int(row["id"]),
        price=float(row["price"]),
        amount=float(row["amount"]),
        total=float(row.get("total") or float(row["price"]) * float(row["amount"])),
        side=str(row.get("side") or "").lower(),
        created_at=str(row.get("created_at") or ""),
    )


def analyze_microstructure(order_book: OrderBook, trades: list[MarketTrade]) -> MicrostructureMetrics:
    best_bid = order_book.bids[0].price if order_book.bids else None
    best_ask = order_book.asks[0].price if order_book.asks else None
    spread_pct = None
    if best_bid is not None and best_ask is not None and best_bid > 0:
        mid = (best_bid + best_ask) / 2
        spread_pct = ((best_ask - best_bid) / mid) * 100 if mid > 0 else None

    bid_quote_total = sum(level.quote for level in order_book.bids)
    ask_quote_total = sum(level.quote for level in order_book.asks)
    ask_bid_ratio = ask_quote_total / bid_quote_total if bid_quote_total > 0 else None

    buy_trades = [trade for trade in trades if trade.side == "buy"]
    sell_trades = [trade for trade in trades if trade.side == "sell"]
    buy_trade_ratio = len(buy_trades) / len(trades) if trades else None

    buy_quote = sum(trade.total for trade in buy_trades)
    sell_quote = sum(trade.total for trade in sell_trades)
    total_quote = buy_quote + sell_quote
    buy_quote_ratio = buy_quote / total_quote if total_quote > 0 else None

    return MicrostructureMetrics(
        best_bid=best_bid,
        best_ask=best_ask,
        spread_pct=spread_pct,
        bid_quote_total=bid_quote_total,
        ask_quote_total=ask_quote_total,
        ask_bid_ratio=ask_bid_ratio,
        recent_trade_count=len(trades),
        buy_trade_ratio=buy_trade_ratio,
        buy_quote_ratio=buy_quote_ratio,
    )


def order_book_to_dict(order_book: OrderBook, limit: int = 10) -> dict[str, Any]:
    asks = order_book.asks[:limit]
    bids = order_book.bids[:limit]
    return {
        "asks": [_level_to_dict(level) for level in asks],
        "bids": [_level_to_dict(level) for level in bids],
        "sequence": order_book.sequence,
    }


def trades_to_dict(trades: list[MarketTrade], limit: int = 20) -> list[dict[str, Any]]:
    return [
        {
            "id": trade.id,
            "price": trade.price,
            "amount": trade.amount,
            "total": trade.total,
            "side": trade.side,
            "created_at": trade.created_at,
        }
        for trade in trades[:limit]
    ]


def microstructure_to_dict(metrics: MicrostructureMetrics) -> dict[str, Any]:
    return {
        "best_bid": metrics.best_bid,
        "best_ask": metrics.best_ask,
        "spread_pct": metrics.spread_pct,
        "bid_quote_total": metrics.bid_quote_total,
        "ask_quote_total": metrics.ask_quote_total,
        "ask_bid_ratio": metrics.ask_bid_ratio,
        "recent_trade_count": metrics.recent_trade_count,
        "buy_trade_ratio": metrics.buy_trade_ratio,
        "buy_quote_ratio": metrics.buy_quote_ratio,
    }


def _parse_level(row: list[Any] | tuple[Any, ...]) -> OrderBookLevel:
    return OrderBookLevel(price=float(row[0]), amount=float(row[1]))


def _level_to_dict(level: OrderBookLevel) -> dict[str, float]:
    return {
        "price": level.price,
        "amount": level.amount,
        "quote": level.quote,
    }
