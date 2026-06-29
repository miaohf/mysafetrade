import { useMemo, useState } from "react";
import { changeTone, fmt, fmtCompact } from "../utils";

function withCumulative(levels) {
  let cumulative = 0;
  return levels.map((row) => {
    const quote = row.quote ?? row.price * row.amount;
    cumulative += quote;
    return { ...row, quote, cumQuote: cumulative };
  });
}

function DepthRow({ row, side, maxCumQuote }) {
  const tone = side === "ask" ? "down" : "up";
  const width = maxCumQuote > 0 ? Math.max(6, (row.cumQuote / maxCumQuote) * 100) : 0;

  return (
    <tr className={`order-book-row ${side}`}>
      <td className={`order-book-price ${tone}`}>{fmt(row.price, 2)}</td>
      <td className="order-book-amount">{fmtCompact(row.amount, 4)}</td>
      <td className="order-book-sum">
        <span className="depth-bar" style={{ width: `${width}%` }} />
        <span className="depth-text">{fmtCompact(row.cumQuote, 2)}</span>
      </td>
    </tr>
  );
}

function DepthViewToggle({ mode, onChange }) {
  return (
    <div className="order-book-views">
      <button
        type="button"
        className={`order-book-view ${mode === "asks" ? "active" : ""}`}
        onClick={() => onChange("asks")}
        aria-label="Asks only"
        title="Asks only"
      >
        <span className="view-icon view-icon--asks" />
      </button>
      <button
        type="button"
        className={`order-book-view ${mode === "both" ? "active" : ""}`}
        onClick={() => onChange("both")}
        aria-label="Asks and bids"
        title="Asks and bids"
      >
        <span className="view-icon view-icon--both" />
      </button>
      <button
        type="button"
        className={`order-book-view ${mode === "bids" ? "active" : ""}`}
        onClick={() => onChange("bids")}
        aria-label="Bids only"
        title="Bids only"
      >
        <span className="view-icon view-icon--bids" />
      </button>
    </div>
  );
}

function OrderBookView({ data, t, depthMode, onDepthModeChange }) {
  const orderBook = data?.order_book || { asks: [], bids: [] };
  const ticker = data?.ticker || {};
  const latestPrice = data?.latest?.price;
  const changeValue = ticker.price_change_percent || "-";
  const changeToneClass = changeTone(changeValue);

  const { asks, bids, maxAskCum, maxBidCum } = useMemo(() => {
    const rawAsks = withCumulative([...(orderBook.asks || [])]);
    const rawBids = withCumulative([...(orderBook.bids || [])]);
    const askRows = [...rawAsks].reverse();
    const bidRows = rawBids;
    return {
      asks: askRows,
      bids: bidRows,
      maxAskCum: Math.max(...askRows.map((row) => row.cumQuote), 1),
      maxBidCum: Math.max(...bidRows.map((row) => row.cumQuote), 1),
    };
  }, [orderBook.asks, orderBook.bids]);

  const showAsks = depthMode === "both" || depthMode === "asks";
  const showBids = depthMode === "both" || depthMode === "bids";
  const showMid = depthMode === "both";

  return (
    <div className="market-view market-view--book">
      <div className="order-book-toolbar">
        <DepthViewToggle mode={depthMode} onChange={onDepthModeChange} />
        <span className="order-book-precision">0.01</span>
      </div>
      <div className="market-view-body">
        <table className="order-book-table">
          <thead>
            <tr>
              <th>{t.priceUsdt}</th>
              <th>{t.amountPrl}</th>
              <th>{t.sumUsdt}</th>
            </tr>
          </thead>
          {showAsks ? (
            <tbody className="order-book-asks">
              {asks.map((row) => (
                <DepthRow key={`ask-${row.price}`} row={row} side="ask" maxCumQuote={maxAskCum} />
              ))}
            </tbody>
          ) : null}
          {showMid ? (
            <tbody className="order-book-mid">
              <tr>
                <td colSpan={3}>
                  <div className="order-book-midline">
                    <span className={`order-book-mid-price ${changeToneClass}`}>{fmt(latestPrice, 2)}</span>
                    <span className={`order-book-mid-change ${changeToneClass}`}>{changeValue}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          ) : null}
          {showBids ? (
            <tbody className="order-book-bids">
              {bids.map((row) => (
                <DepthRow key={`bid-${row.price}`} row={row} side="bid" maxCumQuote={maxBidCum} />
              ))}
            </tbody>
          ) : null}
        </table>
      </div>
    </div>
  );
}

function TradesView({ trades, t }) {
  return (
    <div className="market-view market-view--trades">
      <div className="market-view-body">
        <table className="compact trade-table">
          <thead>
            <tr>
              <th>{t.priceUsdt}</th>
              <th>{t.amountPrl}</th>
              <th>{t.sumUsdt}</th>
              <th>{t.time}</th>
            </tr>
          </thead>
          <tbody>
            {trades.map((trade) => (
              <tr key={trade.id}>
                <td className={trade.side === "buy" ? "up" : "down"}>{fmt(trade.price, 2)}</td>
                <td>{fmtCompact(trade.amount, 4)}</td>
                <td>{fmtCompact(trade.total ?? trade.price * trade.amount, 2)}</td>
                <td>{formatTradeTime(trade.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function MarketActivityPanel({ data, t }) {
  const [panelTab, setPanelTab] = useState("book");
  const [depthMode, setDepthMode] = useState("both");
  const trades = data?.recent_trades || [];

  return (
    <div className="market-activity">
      <div className="market-tabs">
        <button
          type="button"
          className={`market-tab ${panelTab === "book" ? "active" : ""}`}
          onClick={() => setPanelTab("book")}
        >
          {t.orderBook}
        </button>
        <button
          type="button"
          className={`market-tab ${panelTab === "trades" ? "active" : ""}`}
          onClick={() => setPanelTab("trades")}
        >
          {t.marketTrades}
        </button>
      </div>

      {panelTab === "book" ? (
        <OrderBookView data={data} t={t} depthMode={depthMode} onDepthModeChange={setDepthMode} />
      ) : (
        <TradesView trades={trades} t={t} />
      )}
    </div>
  );
}

function formatTradeTime(value) {
  if (!value) {
    return "-";
  }
  const match = value.match(/T(\d{2}:\d{2}:\d{2})/);
  return match ? match[1] : value.slice(11, 19);
}
