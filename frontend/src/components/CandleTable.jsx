import { fmt, fmtCompact, formatTimestamp, maTrendTone, rsiTone, volumeTone } from "../utils";

export default function CandleTable({ points, t, limit = 12, compact = false }) {
  const rows = [...points].slice(-limit).reverse();

  return (
    <div className="table-wrap">
      <table className={compact ? "compact" : ""}>
        <thead>
          <tr>
            <th>{t.time}</th>
            <th>{t.close}</th>
            <th>{t.volume}</th>
            <th>MA7</th>
            <th>MA25</th>
            <th>RSI14</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((point) => (
            <tr key={point.timestamp}>
              <td>{formatTimestamp(point.timestamp)}</td>
              <td>{fmt(point.close, 4)}</td>
              <td className={volumeTone(point.volume_ma ? point.volume / point.volume_ma : null)}>
                {fmtCompact(point.volume, 1)}
              </td>
              <td className={maTrendTone(point.ma7, point.ma25)}>{fmt(point.ma7, 4)}</td>
              <td>{fmt(point.ma25, 4)}</td>
              <td className={rsiTone(point.rsi14)}>{fmt(point.rsi14, 2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
