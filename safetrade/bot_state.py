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
    signal_reason: str
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
