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
  background: "#10161f",
  border: "1px solid #243041",
  borderRadius: 10,
  color: "#edf2f7",
};

export default function RsiChart({ points }) {
  const chartData = points.map((point) => ({
    time: formatChartLabel(point.timestamp),
    rsi14: point.rsi14,
  }));

  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#243041" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: "#8fa0b3", fontSize: 12 }} minTickGap={24} />
          <YAxis domain={[0, 100]} tick={{ fill: "#8fa0b3", fontSize: 12 }} />
          <Tooltip
            contentStyle={tooltipStyle}
            formatter={(value) => [fmt(value, 2), "RSI14"]}
          />
          <ReferenceLine y={70} stroke="#f87171" strokeDasharray="4 4" />
          <ReferenceLine y={30} stroke="#34d399" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="rsi14"
            name="RSI14"
            stroke="#fbbf24"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
