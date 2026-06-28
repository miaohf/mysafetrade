import { fmt } from "../utils";

export default function MaDetail({ data }) {
  const calc = data.ma_calculation || {};
  const strategy = data.strategy || {};

  const lines = [
    `MA7 = (${calc.short_closes?.map((value) => value.toFixed(4)).join(" + ")}) / ${calc.short_window}`,
    `MA7 = ${calc.short_sum?.toFixed(4)} / ${calc.short_window} = ${fmt(calc.short_ma, 4)}`,
    "",
    `MA25 = sum(last ${calc.long_window} closes) / ${calc.long_window}`,
    `MA25 = ${calc.long_sum?.toFixed(4)} / ${calc.long_window} = ${fmt(calc.long_ma, 4)}`,
    "",
    `策略结果: ${strategy.signal} · ${strategy.reason}`,
  ];

  return <div className="formula-box">{lines.join("\n")}</div>;
}
