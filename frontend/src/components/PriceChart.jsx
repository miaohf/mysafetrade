import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
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

export default function PriceChart({ points, t }) {
  const chartData = points.map((point) => ({
    time: formatChartLabel(point.timestamp),
    close: point.close,
    ma7: point.ma7,
    ma25: point.ma25,
  }));

  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 4, right: 8, left: -8, bottom: 0 }}>
          <CartesianGrid stroke="rgba(83, 103, 134, 0.34)" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: "#8291a7", fontSize: 12 }} minTickGap={24} />
          <YAxis
            tick={{ fill: "#8291a7", fontSize: 12 }}
            domain={["auto", "auto"]}
            tickFormatter={(value) => fmt(value, 3)}
          />
          <Tooltip
            contentStyle={tooltipStyle}
            formatter={(value, name) => [fmt(value, 4), name]}
          />
          <Legend wrapperStyle={{ color: "#c8d5e6", paddingTop: 4, fontSize: 11 }} />
          <Line
            type="monotone"
            dataKey="close"
            name={t.closePrice}
            stroke="#dbe6f3"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="ma7"
            name="MA7"
            stroke="#39a2ff"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="ma25"
            name="MA25"
            stroke="#00c087"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
