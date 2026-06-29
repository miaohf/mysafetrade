import { fmt, fmtCompact } from "../utils";

function Item({ label, value, tone = "" }) {
  return (
    <div className="ticker-item">
      <span className="ticker-label">{label}</span>
      <span className={`ticker-value ${tone}`}>{value}</span>
    </div>
  );
}

export default function TickerSummary({ ticker, microstructure, t }) {
  const micro = microstructure || {};

  return (
    <div className="ticker-summary">
      <div className="ticker-summary-title">{t.ticker24h}</div>
      <div className="ticker-grid">
        <Item label={t.open24h} value={fmt(ticker.open, 4)} />
        <Item label={t.high24h} value={fmt(ticker.high, 4)} tone="up" />
        <Item label={t.low24h} value={fmt(ticker.low, 4)} tone="down" />
        <Item label={t.vol24h} value={fmtCompact(ticker.volume, 2)} />
        <Item label={t.bestBid} value={fmt(micro.best_bid, 4)} tone="up" />
        <Item label={t.bestAsk} value={fmt(micro.best_ask, 4)} tone="down" />
        <Item label={t.bidDepth} value={fmtCompact(micro.bid_quote_total, 2)} />
        <Item label={t.askDepth} value={fmtCompact(micro.ask_quote_total, 2)} />
      </div>
    </div>
  );
}
