from __future__ import annotations

from dataclasses import dataclass

from safetrade.strategy import Signal, StrategyDecision


@dataclass(frozen=True)
class Portfolio:
    cash: float
    asset_qty: float = 0.0

    def total_value(self, price: float) -> float:
        return self.cash + self.asset_qty * price


@dataclass(frozen=True)
class RiskDecision:
    approved: bool
    signal: Signal
    quote_amount: float
    reason: str


class RiskManager:
    def __init__(
        self,
        max_position_pct: float,
        max_order_quote: float,
        min_cash_reserve: float,
        min_trade_quote: float,
    ) -> None:
        self.max_position_pct = max_position_pct
        self.max_order_quote = max_order_quote
        self.min_cash_reserve = min_cash_reserve
        self.min_trade_quote = min_trade_quote

    def evaluate(self, portfolio: Portfolio, decision: StrategyDecision) -> RiskDecision:
        price = decision.reference_price

        if decision.signal is Signal.HOLD:
            return RiskDecision(False, Signal.HOLD, 0.0, decision.reason)

        if decision.signal is Signal.BUY:
            return self._evaluate_buy(portfolio, price)

        if decision.signal is Signal.SELL:
            return self._evaluate_sell(portfolio, price)

        return RiskDecision(False, decision.signal, 0.0, "unknown signal")

    def _evaluate_buy(self, portfolio: Portfolio, price: float) -> RiskDecision:
        total_value = portfolio.total_value(price)
        current_position_value = portfolio.asset_qty * price
        max_position_value = total_value * self.max_position_pct
        available_position_room = max(0.0, max_position_value - current_position_value)
        spendable_cash = max(0.0, portfolio.cash - self.min_cash_reserve)
        quote_amount = min(available_position_room, spendable_cash, self.max_order_quote)

        if quote_amount < self.min_trade_quote:
            return RiskDecision(False, Signal.BUY, 0.0, "buy rejected by position/cash limits")

        return RiskDecision(True, Signal.BUY, quote_amount, "buy approved")

    def _evaluate_sell(self, portfolio: Portfolio, price: float) -> RiskDecision:
        position_value = portfolio.asset_qty * price
        quote_amount = min(position_value, self.max_order_quote)

        if quote_amount < self.min_trade_quote:
            return RiskDecision(False, Signal.SELL, 0.0, "sell rejected: no meaningful position")

        return RiskDecision(True, Signal.SELL, quote_amount, "sell approved")
