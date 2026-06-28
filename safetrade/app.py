from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone

from safetrade.broker import OrderResult, PaperBroker
from safetrade.config import Settings, load_settings
from safetrade.market import MarketDataClient, MockMarketDataClient, SafeTradePublicMarketDataClient
from safetrade.risk import Portfolio, RiskManager
from safetrade.strategy import MovingAverageCrossStrategy, StrategyDecision

logger = logging.getLogger("safetrade")


@dataclass(frozen=True)
class EngineResult:
    strategy: StrategyDecision
    order: OrderResult
    portfolio: Portfolio


class TradingEngine:
    def __init__(
        self,
        settings: Settings,
        market: MarketDataClient,
        strategy: MovingAverageCrossStrategy,
        broker: PaperBroker,
        risk: RiskManager,
    ) -> None:
        self.settings = settings
        self.market = market
        self.strategy = strategy
        self.broker = broker
        self.risk = risk

    def run_once(self) -> EngineResult:
        candles = self.market.get_recent_candles(self.settings.symbol, limit=self.settings.candle_limit)
        strategy_decision = self.strategy.decide(candles)
        risk_decision = self.risk.evaluate(self.broker.portfolio, strategy_decision)
        order = self.broker.execute_market_order(risk_decision, strategy_decision.reference_price)

        return EngineResult(
            strategy=strategy_decision,
            order=order,
            portfolio=self.broker.portfolio,
        )


def build_engine(settings: Settings) -> TradingEngine:
    if settings.market_data_source == "safetrade_public":
        market: MarketDataClient = SafeTradePublicMarketDataClient(
            api_base_url=settings.api_base_url,
            period=settings.kline_period,
        )
    else:
        market = MockMarketDataClient(start_price=settings.mock_start_price)

    strategy = MovingAverageCrossStrategy()
    broker = PaperBroker(
        Portfolio(cash=settings.initial_cash, asset_qty=settings.initial_asset_qty),
        fee_rate=settings.fee_rate,
    )
    risk = RiskManager(
        max_position_pct=settings.max_position_pct,
        max_order_quote=settings.max_order_quote,
        min_cash_reserve=settings.min_cash_reserve,
        min_trade_quote=settings.min_trade_quote,
    )

    return TradingEngine(settings, market, strategy, broker, risk)


def run_daemon(engine: TradingEngine) -> None:
    settings = engine.settings
    logger.info(
        "daemon_started exchange=%s symbol=%s market_id=%s source=%s interval=%.1fs paper_trading=%s",
        settings.exchange,
        settings.symbol,
        settings.market_id,
        settings.market_data_source,
        settings.loop_interval_seconds,
        settings.paper_trading,
    )

    while True:
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            result = engine.run_once()
            _log_result(started_at, settings, result)
        except Exception:
            logger.exception("cycle_failed started_at=%s", started_at)

        if settings.run_once:
            logger.info("daemon_stopped reason=run_once")
            return

        time.sleep(settings.loop_interval_seconds)


def _log_result(started_at: str, settings: Settings, result: EngineResult) -> None:
    portfolio_value = result.portfolio.total_value(result.strategy.reference_price)
    logger.info(
        "cycle_completed started_at=%s symbol=%s market_id=%s price=%.8f signal=%s "
        "signal_reason=%r order_executed=%s order_side=%s order_quote=%.2f "
        "order_base=%.8f fee=%.4f order_reason=%r cash=%.2f asset_qty=%.8f value=%.2f",
        started_at,
        settings.symbol,
        settings.market_id,
        result.strategy.reference_price,
        result.strategy.signal.value,
        result.strategy.reason,
        result.order.executed,
        result.order.signal.value,
        result.order.quote_amount,
        result.order.base_amount,
        result.order.fee,
        result.order.reason,
        result.portfolio.cash,
        result.portfolio.asset_qty,
        portfolio_value,
    )


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def main() -> None:
    configure_logging()
    settings = load_settings()

    if not settings.paper_trading:
        raise RuntimeError("Live trading is not implemented yet. Set PAPER_TRADING=true.")

    engine = build_engine(settings)
    run_daemon(engine)


if __name__ == "__main__":
    main()
