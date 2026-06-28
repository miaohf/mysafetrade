import { changeTone, fmt, maTrendTone, rsiTone } from "../utils";

export default function StatsGrid({ data, t }) {
  const latest = data.latest || {};
  const ticker = data.ticker || {};
  const changeValue = ticker.price_change_percent || "-";

  const items = [
    { label: t.latestPrice, value: fmt(latest.price, 4) },
    { label: "MA7", value: fmt(latest.ma7, 4), tone: maTrendTone(latest.ma7, latest.ma25) },
    { label: "MA25", value: fmt(latest.ma25, 4) },
    { label: "RSI14", value: fmt(latest.rsi14, 2), tone: rsiTone(latest.rsi14) },
    { label: t.change24h, value: changeValue, tone: changeTone(changeValue), labelTone: changeTone(changeValue) },
  ];

  return (
    <div className="stats-grid">
      {items.map((item) => (
        <div className="stat-card" key={item.label}>
          <div className={`stat-label ${item.labelTone || ""}`}>{item.label}</div>
          <div className={`stat-value ${item.tone || ""}`}>{item.value}</div>
        </div>
      ))}
    </div>
  );
}
