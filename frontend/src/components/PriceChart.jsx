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
  background: "#10161f",
  border: "1px solid #243041",
  borderRadius: 10,
  color: "#edf2f7",
};

export default function PriceChart({ points }) {
  const chartData = points.map((point) => ({
    time: formatChartLabel(point.timestamp),
    close: point.close,
    ma7: point.ma7,
    ma25: point.ma25,
  }));

  return (
    <div className="chart-wrap">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid stroke="#243041" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="time" tick={{ fill: "#8fa0b3", fontSize: 12 }} minTickGap={24} />
          <YAxis
            tick={{ fill: "#8fa0b3", fontSize: 12 }}
            domain={["auto", "auto"]}
            tickFormatter={(value) => fmt(value, 3)}
          />
          <Tooltip
            contentStyle={tooltipStyle}
            formatter={(value, name) => [fmt(value, 4), name]}
          />
          <Legend wrapperStyle={{ color: "#c8d7e6", paddingTop: 12 }} />
          <Line
            type="monotone"
            dataKey="close"
            name="收盘价"
            stroke="#edf2f7"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          <Line
            type="monotone"
            dataKey="ma7"
            name="MA7"
            stroke="#5eb3ff"
            strokeWidth={2}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="ma25"
            name="MA25"
            stroke="#34d399"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
