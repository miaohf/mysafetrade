import { changeTone, fmt, fmtCompact, maTrendTone, rsiTone, volumeTone } from "../utils";

export default function StatsGrid({ data, t }) {
  const latest = data.latest || {};
  const ticker = data.ticker || {};
  const strategy = data.strategy || {};
  const changeValue = ticker.price_change_percent || "-";
  const volumeRatio = latest.volume_ratio;
  const volumeThreshold = strategy.min_volume_ratio || 1;

  const items = [
    { label: t.latestPrice, value: fmt(latest.price, 4) },
    { label: t.change24h, value: changeValue, tone: changeTone(changeValue), labelTone: changeTone(changeValue) },
    { label: "MA7", value: fmt(latest.ma7, 4), tone: maTrendTone(latest.ma7, latest.ma25) },
    { label: "RSI14", value: fmt(latest.rsi14, 2), tone: rsiTone(latest.rsi14) },
    {
      label: t.volumeRatio,
      value: volumeRatio === null || volumeRatio === undefined ? "-" : `${fmt(volumeRatio, 2)}x`,
      tone: volumeTone(volumeRatio, volumeThreshold),
      labelTone: volumeTone(volumeRatio, volumeThreshold),
    },
    { label: t.quoteVolume, value: fmtCompact(latest.quote_volume, 2) },
  ];

  return (
    <div className="stats-strip">
      {items.map((item) => (
        <div className="stat-item" key={item.label}>
          <span className={`stat-label ${item.labelTone || ""}`}>{item.label}</span>
          <span className={`stat-value ${item.tone || ""}`}>{item.value}</span>
        </div>
      ))}
    </div>
  );
}
