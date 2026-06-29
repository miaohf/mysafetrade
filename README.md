# SafeTrade

SafeTrade is a starter automated trading project for SafeTrade.com. Phase 1 is limited to `PRL/USDT` paper trading.

## Architecture

```text
backend/           Python backend
  ├─ safetrade/    trading bot + REST API package
  ├─ main.py       entry point
  └─ .env          backend configuration

frontend/          React dashboard (display only)
  └─ calls http://127.0.0.1:8787/api/*
```

- **Backend**: `cd backend && uv run python main.py` starts the trading bot and API together.
- **Frontend**: `frontend/` is a separate React app for charts and analysis display.

## Safety Rules

- Keep real credentials in `.env`; never commit `.env`.
- Keep `PAPER_TRADING=true` until a real exchange adapter and tests are added.
- Do not enable withdrawal permission for trading API keys.
- Phase 1 only allows `PRL/USDT`.
- Every strategy signal must pass risk checks before an order is created.

## Backend Setup

```bash
cd backend
cp env.example .env
uv sync
uv run python main.py
```

The backend runs continuously. Stop it with `Ctrl+C`.

API endpoints:

- `GET /api/health`
- `GET /api/analysis`

Default API URL: `http://127.0.0.1:8787`

## Frontend Setup

Development mode with hot reload:

```bash
# terminal 1: backend
cd backend
uv run python main.py

# terminal 2: frontend
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` to the backend.

Production build:

```bash
cd frontend
npm install
npm run build
npm run preview
```

## Recommended `.env`

```env
EXCHANGE=safetrade
EXCHANGE_BASE_URL=https://safetrade.com
API_BASE_URL=https://safe.trade/api/v2
SYMBOL=PRL/USDT
ALLOWED_SYMBOLS=PRL/USDT
MARKET_DATA_SOURCE=safetrade_public
KLINE_PERIOD=60
CANDLE_LIMIT=60
LOOP_INTERVAL_SECONDS=300
RUN_ONCE=false
LOG_FILE=logs/safetrade.log
LOG_LEVEL=INFO
ENABLE_API=true
API_PORT=8787
PAPER_TRADING=true
INITIAL_CASH=99
INITIAL_ASSET_QTY=250
MAX_POSITION_PCT=0.5
MAX_ORDER_QUOTE=5
MIN_CASH_RESERVE=40
MIN_TRADE_QUOTE=5
STRATEGY_VOLUME_WINDOW=20
STRATEGY_MIN_VOLUME_RATIO=1.05
STRATEGY_MIN_QUOTE_VOLUME=50
STRATEGY_MAX_BUY_RSI=75
ORDER_BOOK_LIMIT=10
RECENT_TRADES_LIMIT=20
STRATEGY_MAX_SPREAD_PCT=2.0
STRATEGY_MAX_ASK_BID_RATIO=1.5
STRATEGY_MIN_BUY_TRADE_RATIO=0.55
```

## Environment Variables

- `ENABLE_API`: start REST API with the trading bot, defaults to `true`.
- `API_PORT`: backend API port, defaults to `8787`.
- `LOOP_INTERVAL_SECONDS`: seconds between each trading analysis cycle.
- `RUN_ONCE`: set to `true` for one cycle during testing.
- `LOG_FILE`: file path for persistent logs.
- `LOG_LEVEL`: logging level.
- `PAPER_TRADING`: must be `true` for now.
- `INITIAL_CASH`: simulated account cash balance.
- `INITIAL_ASSET_QTY`: simulated PRL balance.
- `MAX_POSITION_PCT`: maximum portfolio value allowed in one asset.
- `MAX_ORDER_QUOTE`: maximum quote currency amount per order.
- `MIN_CASH_RESERVE`: cash that must remain after buys.
- `MIN_TRADE_QUOTE`: minimum order size.
- `STRATEGY_VOLUME_WINDOW`: previous candle count used as the volume baseline.
- `STRATEGY_MIN_VOLUME_RATIO`: buy signals require current volume / average volume to meet this ratio.
- `STRATEGY_MIN_QUOTE_VOLUME`: buy signals require enough estimated USDT turnover in the latest candle.
- `STRATEGY_MAX_BUY_RSI`: buy signals are blocked when RSI is at or above this value.
- `ORDER_BOOK_LIMIT`: number of order book levels fetched from the public API.
- `RECENT_TRADES_LIMIT`: number of recent market trades fetched for microstructure analysis.
- `STRATEGY_MAX_SPREAD_PCT`: buy signals require bid/ask spread to stay below this percentage.
- `STRATEGY_MAX_ASK_BID_RATIO`: buy signals require ask-side depth not to dominate bid-side depth too much.
- `STRATEGY_MIN_BUY_TRADE_RATIO`: buy signals require recent market trades to show enough buy-side pressure.

## Current Flow

1. Backend reads `PRL/USDT` ticker, k-line, order book, and recent trades from SafeTrade public API.
2. `MovingAverageCrossStrategy` starts from MA7/MA25 crosses, then confirms buy signals with volume, quote volume, RSI, spread, depth, and recent trade pressure filters.
3. `RiskManager` approves or rejects the signal.
4. `PaperBroker` simulates the order and updates the portfolio.
5. Frontend reads `/api/analysis` and renders charts and indicators.

## Dependency Management

Python:

```bash
cd backend
uv add package-name
```

Frontend:

```bash
cd frontend
npm install
```
