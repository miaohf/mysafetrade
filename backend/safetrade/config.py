from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EXCHANGE = "safetrade"
DEFAULT_EXCHANGE_BASE_URL = "https://safetrade.com"
DEFAULT_API_BASE_URL = "https://safe.trade/api/v2"
DEFAULT_SYMBOL = "PRL/USDT"
DEFAULT_ALLOWED_SYMBOLS = (DEFAULT_SYMBOL,)
DEFAULT_MARKET_DATA_SOURCE = "safetrade_public"
BACKEND_ROOT = Path(__file__).resolve().parent.parent


def resolve_backend_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return BACKEND_ROOT / candidate


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _env(name: str, default: str = "") -> str:
    return os.getenv(name) or os.getenv(name.lower()) or default


def _env_bool(name: str, default: bool) -> bool:
    value = _env(name, str(default)).lower()
    return value in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
    value = _env(name, str(default))
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got {value!r}") from exc


def _env_list(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = _env(name)
    if not value:
        return default

    return tuple(item.strip() for item in value.split(",") if item.strip())


def normalize_symbol(symbol: str) -> str:
    return symbol.replace("-", "/").replace("_", "/").upper()


@dataclass(frozen=True)
class Settings:
    exchange: str
    exchange_base_url: str
    api_base_url: str
    api_key: str
    api_secret: str
    kid: str
    symbol: str
    allowed_symbols: tuple[str, ...]
    market_data_source: str
    kline_period: int
    candle_limit: int
    loop_interval_seconds: float
    run_once: bool
    log_file: str
    log_level: str
    enable_api: bool
    api_port: int
    paper_trading: bool
    initial_cash: float
    initial_asset_qty: float
    fee_rate: float
    mock_start_price: float
    max_position_pct: float
    max_order_quote: float
    min_cash_reserve: float
    min_trade_quote: float
    strategy_volume_window: int
    strategy_min_volume_ratio: float
    strategy_min_quote_volume: float
    strategy_max_buy_rsi: float
    order_book_limit: int
    recent_trades_limit: int
    strategy_max_spread_pct: float
    strategy_max_ask_bid_ratio: float
    strategy_min_buy_trade_ratio: float

    @property
    def has_api_credentials(self) -> bool:
        return bool(self.api_key and self.api_secret)

    @property
    def market_id(self) -> str:
        return self.symbol.replace("/", "").lower()

    @property
    def log_file_path(self) -> Path:
        return resolve_backend_path(self.log_file)

    def validate(self) -> None:
        if self.exchange != DEFAULT_EXCHANGE:
            raise ValueError(f"only {DEFAULT_EXCHANGE!r} is supported in phase 1")

        if self.symbol not in self.allowed_symbols:
            allowed = ", ".join(self.allowed_symbols)
            raise ValueError(f"symbol {self.symbol!r} is not allowed in phase 1; use one of: {allowed}")

        if self.market_data_source not in {"safetrade_public", "mock"}:
            raise ValueError("MARKET_DATA_SOURCE must be 'safetrade_public' or 'mock'")

        if self.strategy_volume_window <= 0:
            raise ValueError("STRATEGY_VOLUME_WINDOW must be positive")

        if self.strategy_min_volume_ratio < 0:
            raise ValueError("STRATEGY_MIN_VOLUME_RATIO must not be negative")

        if self.strategy_min_quote_volume < 0:
            raise ValueError("STRATEGY_MIN_QUOTE_VOLUME must not be negative")

        if self.order_book_limit <= 0:
            raise ValueError("ORDER_BOOK_LIMIT must be positive")

        if self.recent_trades_limit <= 0:
            raise ValueError("RECENT_TRADES_LIMIT must be positive")


def load_settings(env_path: str | Path | None = None) -> Settings:
    env_file = Path(env_path) if env_path is not None else BACKEND_ROOT / ".env"
    _load_dotenv(env_file)

    settings = Settings(
        exchange=_env("EXCHANGE", DEFAULT_EXCHANGE).lower(),
        exchange_base_url=_env("EXCHANGE_BASE_URL", DEFAULT_EXCHANGE_BASE_URL),
        api_base_url=_env("API_BASE_URL", DEFAULT_API_BASE_URL),
        api_key=_env("API_KEY"),
        api_secret=_env("API_SECRET"),
        kid=_env("KID"),
        symbol=normalize_symbol(_env("SYMBOL", DEFAULT_SYMBOL)),
        allowed_symbols=tuple(normalize_symbol(symbol) for symbol in _env_list("ALLOWED_SYMBOLS", DEFAULT_ALLOWED_SYMBOLS)),
        market_data_source=_env("MARKET_DATA_SOURCE", DEFAULT_MARKET_DATA_SOURCE).lower(),
        kline_period=int(_env_float("KLINE_PERIOD", 60)),
        candle_limit=int(_env_float("CANDLE_LIMIT", 60)),
        loop_interval_seconds=_env_float("LOOP_INTERVAL_SECONDS", 60),
        run_once=_env_bool("RUN_ONCE", False),
        log_file=_env("LOG_FILE", "logs/safetrade.log"),
        log_level=_env("LOG_LEVEL", "INFO").upper(),
        enable_api=_env_bool("ENABLE_API", True),
        api_port=int(_env_float("API_PORT", _env_float("DASHBOARD_PORT", 8787))),
        paper_trading=_env_bool("PAPER_TRADING", True),
        initial_cash=_env_float("INITIAL_CASH", 99),
        initial_asset_qty=_env_float("INITIAL_ASSET_QTY", 250),
        fee_rate=_env_float("FEE_RATE", 0.001),
        mock_start_price=_env_float("MOCK_START_PRICE", 0.54),
        max_position_pct=_env_float("MAX_POSITION_PCT", 0.2),
        max_order_quote=_env_float("MAX_ORDER_QUOTE", 10),
        min_cash_reserve=_env_float("MIN_CASH_RESERVE", 20),
        min_trade_quote=_env_float("MIN_TRADE_QUOTE", 5),
        strategy_volume_window=int(_env_float("STRATEGY_VOLUME_WINDOW", 20)),
        strategy_min_volume_ratio=_env_float("STRATEGY_MIN_VOLUME_RATIO", 1.05),
        strategy_min_quote_volume=_env_float("STRATEGY_MIN_QUOTE_VOLUME", 50),
        strategy_max_buy_rsi=_env_float("STRATEGY_MAX_BUY_RSI", 75),
        order_book_limit=int(_env_float("ORDER_BOOK_LIMIT", 20)),
        recent_trades_limit=int(_env_float("RECENT_TRADES_LIMIT", 20)),
        strategy_max_spread_pct=_env_float("STRATEGY_MAX_SPREAD_PCT", 2.0),
        strategy_max_ask_bid_ratio=_env_float("STRATEGY_MAX_ASK_BID_RATIO", 1.5),
        strategy_min_buy_trade_ratio=_env_float("STRATEGY_MIN_BUY_TRADE_RATIO", 0.55),
    )
    settings.validate()
    return settings
