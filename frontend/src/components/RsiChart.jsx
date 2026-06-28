import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatChartLabel, fmt } from "../utils";

const tooltipStyle = {
  background: "#172234",
  border: "1px solid rgba(83, 103, 134, 0.54)",
  borderRadius: 8,
  color: "#dbe6f3",
};

export default function RsiChart({ points }) {
  const chartData = points.map((point) => ({
    time: formatChartLabel(point.timestamp),
    rsi14: point.rsi14,
  }));

  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
          <CartesianGrid stroke="rgba(83, 103, 134, 0.34)" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: "#8291a7", fontSize: 12 }} minTickGap={24} />
          <YAxis domain={[0, 100]} tick={{ fill: "#8291a7", fontSize: 12 }} />
          <Tooltip
            contentStyle={tooltipStyle}
            formatter={(value) => [fmt(value, 2), "RSI14"]}
          />
          <ReferenceLine y={70} stroke="#f0525f" strokeDasharray="4 4" />
          <ReferenceLine y={30} stroke="#00c087" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="rsi14"
            name="RSI14"
            stroke="#f4bd50"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
