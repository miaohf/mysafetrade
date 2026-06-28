from __future__ import annotations

import json
import logging
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from safetrade.analysis import build_market_analysis
from safetrade.bot_state import get_cycle
from safetrade.config import Settings
from safetrade.market import MockMarketDataClient, SafeTradePublicMarketDataClient
from safetrade.strategy import MovingAverageCrossStrategy

logger = logging.getLogger("safetrade.api")


def fetch_analysis(settings: Settings) -> dict[str, Any]:
    strategy = MovingAverageCrossStrategy()
    if settings.market_data_source == "safetrade_public":
        market = SafeTradePublicMarketDataClient(
            api_base_url=settings.api_base_url,
            period=settings.kline_period,
        )
        ticker = market.get_ticker(settings.market_id)
    else:
        market = MockMarketDataClient(start_price=settings.mock_start_price)
        ticker = {
            "last": str(settings.mock_start_price),
            "high": str(settings.mock_start_price),
            "low": str(settings.mock_start_price),
            "open": str(settings.mock_start_price),
            "price_change_percent": "0.00%",
        }

    candles = market.get_recent_candles(settings.symbol, limit=settings.candle_limit)
    analysis = build_market_analysis(candles, ticker, strategy)
    analysis["meta"] = {
        "symbol": settings.symbol,
        "market_id": settings.market_id,
        "kline_period": settings.kline_period,
        "candle_limit": settings.candle_limit,
        "market_data_source": settings.market_data_source,
    }
    analysis["bot_cycle"] = get_cycle()
    return analysis


class ApiHandler(BaseHTTPRequestHandler):
    settings: Settings

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        try:
            if path == "/api/health":
                self._send_json({"status": "ok", "symbol": self.settings.symbol})
                return

            if path == "/api/analysis":
                self._send_json(fetch_analysis(self.settings))
                return

            self._send_json({"error": "not found", "path": path}, status=HTTPStatus.NOT_FOUND)
        except (BrokenPipeError, ConnectionResetError):
            logger.debug("client disconnected path=%s", path)

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            logger.debug("client disconnected during request")

    def log_message(self, format: str, *args: Any) -> None:
        logger.info("%s - %s", self.address_string(), format % args)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._send_cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            logger.debug("client disconnected while sending response")


def start_api_server(settings: Settings, host: str = "127.0.0.1") -> ThreadingHTTPServer:
    handler = type("ConfiguredApiHandler", (ApiHandler,), {"settings": settings})
    server = ThreadingHTTPServer((host, settings.api_port), handler)
    logger.info(
        "api_started url=http://%s:%s endpoints=/api/health,/api/analysis symbol=%s",
        host,
        settings.api_port,
        settings.symbol,
    )
    return server


def start_api_in_background(settings: Settings, host: str = "127.0.0.1") -> threading.Thread:
    server = start_api_server(settings, host=host)

    def _serve() -> None:
        try:
            server.serve_forever()
        except Exception:
            logger.exception("api_failed")
        finally:
            server.server_close()

    thread = threading.Thread(target=_serve, name="safetrade-api", daemon=True)
    thread.start()
    return thread
