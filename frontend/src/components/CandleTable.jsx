import { fmt, formatTimestamp } from "../utils";

export default function CandleTable({ points }) {
  const rows = [...points].slice(-12).reverse();

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>时间</th>
            <th>收盘</th>
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
              <td>{fmt(point.ma7, 4)}</td>
              <td>{fmt(point.ma25, 4)}</td>
              <td>{fmt(point.rsi14, 2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
