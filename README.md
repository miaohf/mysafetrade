# SafeTrade

SafeTrade is a starter automated trading project for SafeTrade.com. Phase 1 is limited to `PRL/USDT` paper trading: it reads SafeTrade public market data, produces a strategy signal, applies risk checks, and simulates a market order.

## Safety Rules

- Keep real credentials in `.env`; never commit `.env`.
- Keep `PAPER_TRADING=true` until a real exchange adapter and tests are added.
- Do not enable withdrawal permission for trading API keys.
- Phase 1 only allows `PRL/USDT`.
- Every strategy signal must pass risk checks before an order is created.

## Setup

```bash
cp env.example .env
uv sync
uv run python main.py
```

If you already created `.env`, keep it and update only the optional trading settings you need.

For a 99 USDT account, start conservatively:

```env
EXCHANGE=safetrade
EXCHANGE_BASE_URL=https://safetrade.com
API_BASE_URL=https://safe.trade/api/v2
SYMBOL=PRL/USDT
ALLOWED_SYMBOLS=PRL/USDT
MARKET_DATA_SOURCE=safetrade_public
KLINE_PERIOD=60
CANDLE_LIMIT=60
PAPER_TRADING=true
INITIAL_CASH=99
INITIAL_ASSET_QTY=250
MAX_POSITION_PCT=0.2
MAX_ORDER_QUOTE=10
MIN_CASH_RESERVE=20
MIN_TRADE_QUOTE=5
```

## Environment Variables

- `EXCHANGE`: exchange name, fixed to `safetrade` in phase 1.
- `EXCHANGE_BASE_URL`: SafeTrade website base URL, defaults to `https://safetrade.com`.
- `API_BASE_URL`: SafeTrade public API URL, defaults to `https://safe.trade/api/v2`.
- `API_KEY`: exchange API key, currently not used by paper trading.
- `API_SECRET`: exchange API secret, currently not used by paper trading.
- `KID`: optional key id if your exchange requires it.
- `SYMBOL`: trading symbol, fixed to `PRL/USDT` in phase 1.
- `ALLOWED_SYMBOLS`: symbol allowlist, fixed to `PRL/USDT` in phase 1.
- `MARKET_DATA_SOURCE`: use `safetrade_public` for real public market data, or `mock` for local generated data.
- `KLINE_PERIOD`: SafeTrade k-line period, defaults to hourly candles with `60`.
- `CANDLE_LIMIT`: number of candles used by the strategy.
- `PAPER_TRADING`: must be `true` for now.
- `INITIAL_CASH`: simulated account cash balance.
- `INITIAL_ASSET_QTY`: simulated PRL balance.
- `FEE_RATE`: simulated trading fee rate.
- `MOCK_START_PRICE`: mock PRL price used by local paper trading.
- `MAX_POSITION_PCT`: maximum portfolio value allowed in one asset.
- `MAX_ORDER_QUOTE`: maximum quote currency amount per order.
- `MIN_CASH_RESERVE`: cash that must remain after buys.
- `MIN_TRADE_QUOTE`: minimum order size.

## Current Flow

1. `SafeTradePublicMarketDataClient` reads `PRL/USDT` ticker and k-line data from SafeTrade public API.
2. `MovingAverageCrossStrategy` returns `buy`, `sell`, or `hold`.
3. `RiskManager` approves or rejects the signal.
4. `PaperBroker` simulates the order and updates the portfolio.

## Dependency Management

This project uses `uv` and `pyproject.toml` for dependencies. Add future packages with:

```bash
uv add package-name
```

Run local commands through uv:

```bash
uv run python main.py
uv run python -m compileall safetrade main.py
```

## Next Steps

- Add a real SafeTrade market data adapter for `PRL/USDT`.
- Add historical data backtesting before live trading.
- Add structured logs for signals, decisions, and orders.
- Add tests for strategy, risk checks, and broker accounting.
