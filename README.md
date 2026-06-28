# SafeTrade

SafeTrade is a starter automated trading project for SafeTrade.com. Phase 1 is limited to `PRL/USDT` paper trading.

## Architecture

```text
frontend/          React dashboard (display only)
  └─ calls http://127.0.0.1:8787/api/*

safetrade/         Python backend
  ├─ trading bot   paper trading daemon
  └─ api_server    REST API for the frontend
```

- **Backend**: `uv run python main.py` starts the trading bot and API together.
- **Frontend**: `frontend/` is a separate React app for charts and analysis display.

## Safety Rules

- Keep real credentials in `.env`; never commit `.env`.
- Keep `PAPER_TRADING=true` until a real exchange adapter and tests are added.
- Do not enable withdrawal permission for trading API keys.
- Phase 1 only allows `PRL/USDT`.
- Every strategy signal must pass risk checks before an order is created.

## Backend Setup

```bash
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

## Current Flow

1. Backend reads `PRL/USDT` ticker and k-line data from SafeTrade public API.
2. `MovingAverageCrossStrategy` returns `buy`, `sell`, or `hold`.
3. `RiskManager` approves or rejects the signal.
4. `PaperBroker` simulates the order and updates the portfolio.
5. Frontend reads `/api/analysis` and renders charts and indicators.

## Dependency Management

Python:

```bash
uv add package-name
```

Frontend:

```bash
cd frontend
npm install
```
