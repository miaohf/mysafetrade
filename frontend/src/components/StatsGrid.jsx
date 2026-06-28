import { fmt, signalTone } from "../utils";

export default function StatsGrid({ data }) {
  const latest = data.latest || {};
  const ticker = data.ticker || {};
  const strategy = data.strategy || {};

  const items = [
    { label: "最新价", value: fmt(latest.price, 4) },
    { label: "MA7", value: fmt(latest.ma7, 4) },
    { label: "MA25", value: fmt(latest.ma25, 4) },
    { label: "RSI14", value: fmt(latest.rsi14, 2) },
    { label: "24h 涨跌", value: ticker.price_change_percent || "-" },
    {
      label: "策略信号",
      value: (strategy.signal || "-").toUpperCase(),
      tone: signalTone(strategy.signal),
    },
  ];

  return (
    <div className="stats-grid">
      {items.map((item) => (
        <div className="stat-card" key={item.label}>
          <div className="stat-label">{item.label}</div>
          <div className={`stat-value ${item.tone || ""}`}>{item.value}</div>
        </div>
      ))}
    </div>
  );
}
