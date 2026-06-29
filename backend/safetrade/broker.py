from __future__ import annotations

from dataclasses import dataclass

from safetrade.risk import Portfolio, RiskDecision
from safetrade.strategy import Signal


@dataclass(frozen=True)
class OrderResult:
    executed: bool
    signal: Signal
    price: float
    quote_amount: float
    base_amount: float
    fee: float
    reason: str


class PaperBroker:
    def __init__(self, portfolio: Portfolio, fee_rate: float = 0.001) -> None:
        self.portfolio = portfolio
        self.fee_rate = fee_rate

    def execute_market_order(self, decision: RiskDecision, price: float) -> OrderResult:
        if not decision.approved:
            return OrderResult(False, decision.signal, price, 0.0, 0.0, 0.0, decision.reason)

        if decision.signal is Signal.BUY:
            return self._buy(decision.quote_amount, price)

        if decision.signal is Signal.SELL:
            return self._sell(decision.quote_amount, price)

        return OrderResult(False, decision.signal, price, 0.0, 0.0, 0.0, "unsupported order")

    def _buy(self, quote_amount: float, price: float) -> OrderResult:
        fee = quote_amount * self.fee_rate
        total_cost = quote_amount + fee

        if total_cost > self.portfolio.cash:
            return OrderResult(False, Signal.BUY, price, 0.0, 0.0, 0.0, "insufficient cash")

        base_amount = quote_amount / price
        self.portfolio = Portfolio(
            cash=self.portfolio.cash - total_cost,
            asset_qty=self.portfolio.asset_qty + base_amount,
        )

        return OrderResult(True, Signal.BUY, price, quote_amount, base_amount, fee, "paper buy filled")

    def _sell(self, quote_amount: float, price: float) -> OrderResult:
        base_amount = min(self.portfolio.asset_qty, quote_amount / price)
        gross_quote = base_amount * price
        fee = gross_quote * self.fee_rate

        if base_amount <= 0:
            return OrderResult(False, Signal.SELL, price, 0.0, 0.0, 0.0, "no asset to sell")

        self.portfolio = Portfolio(
            cash=self.portfolio.cash + gross_quote - fee,
            asset_qty=self.portfolio.asset_qty - base_amount,
        )

        return OrderResult(True, Signal.SELL, price, gross_quote, base_amount, fee, "paper sell filled")
