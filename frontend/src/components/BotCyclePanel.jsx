import { fmt, formatTimestamp, sideTone, signalTone } from "../utils";

function Item({ label, value, tone = "" }) {
  return (
    <div className="bot-item">
      <div className="bot-label">{label}</div>
      <div className={`bot-value ${tone}`}>{value}</div>
    </div>
  );
}

export default function BotCyclePanel({ botCycle, t, compact = false }) {
  if (!botCycle) {
    return <div className="bot-empty">{t.botWaiting}</div>;
  }

  return (
    <div className={`bot-grid${compact ? " compact" : ""}`}>
      <Item label={t.analysisTime} value={formatTimestamp(botCycle.started_at)} />
      <Item label={t.symbol} value={`${botCycle.symbol} (${botCycle.market_id})`} />
      <Item label={t.referencePrice} value={fmt(botCycle.price, 4)} />
      <Item
        label={t.strategySignal}
        value={(botCycle.signal || "-").toUpperCase()}
        tone={signalTone(botCycle.signal)}
      />
      <Item label={t.signalReason} value={botCycle.signal_reason || "-"} />
      <Item
        label={t.orderExecuted}
        value={botCycle.order_executed ? t.yes : t.no}
        tone={botCycle.order_executed ? "up" : ""}
      />
      <Item
        label={t.orderSide}
        value={(botCycle.order_side || "-").toUpperCase()}
        tone={sideTone(botCycle.order_side)}
      />
      <Item label={t.orderQuote} value={fmt(botCycle.order_quote, 2)} />
      <Item label={t.orderBase} value={fmt(botCycle.order_base, 8)} />
      <Item label={t.fee} value={fmt(botCycle.fee, 4)} />
      <Item label={t.orderReason} value={botCycle.order_reason || "-"} />
      <Item label={t.cash} value={fmt(botCycle.cash, 2)} />
      <Item label={t.assetQty} value={fmt(botCycle.asset_qty, 8)} />
      <Item label={t.totalValue} value={fmt(botCycle.value, 2)} />
      <Item
        label={t.runMode}
        value={
          botCycle.paper_trading
            ? `${t.paperTrading} · ${t.every} ${botCycle.loop_interval_seconds}s`
            : t.liveTrading
        }
      />
    </div>
  );
}
