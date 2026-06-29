from __future__ import annotations

import threading
from dataclasses import asdict, dataclass
from typing import Any

_lock = threading.Lock()
_latest_cycle: dict[str, Any] | None = None


@dataclass(frozen=True)
class BotCycleSnapshot:
    started_at: str
    symbol: str
    market_id: str
    price: float
    signal: str
    raw_signal: str
    signal_reason: str
    rsi14: float | None
    volume: float
    average_volume: float | None
    volume_ratio: float | None
    min_volume_ratio: float
    quote_volume: float
    average_quote_volume: float | None
    min_quote_volume: float
    spread_pct: float | None
    ask_bid_ratio: float | None
    buy_quote_ratio: float | None
    order_executed: bool
    order_side: str
    order_quote: float
    order_base: float
    fee: float
    order_reason: str
    cash: float
    asset_qty: float
    value: float
    paper_trading: bool
    loop_interval_seconds: float


def update_cycle(snapshot: BotCycleSnapshot) -> None:
    global _latest_cycle
    with _lock:
        _latest_cycle = asdict(snapshot)


def get_cycle() -> dict[str, Any] | None:
    with _lock:
        if _latest_cycle is None:
            return None
        return dict(_latest_cycle)
