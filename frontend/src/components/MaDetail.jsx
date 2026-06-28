import { fmt, signalTone } from "../utils";
import { template } from "../i18n";

export default function MaDetail({ data, t, compact = false }) {
  const calc = data.ma_calculation || {};
  const strategy = data.strategy || {};

  const lines = [
    `MA7 = (${calc.short_closes?.map((value) => value.toFixed(4)).join(" + ")}) / ${calc.short_window}`,
    `MA7 = ${calc.short_sum?.toFixed(4)} / ${calc.short_window} = ${fmt(calc.short_ma, 4)}`,
    "",
    `MA25 = ${template(t.ma25Formula, { window: calc.long_window })}`,
    `MA25 = ${calc.long_sum?.toFixed(4)} / ${calc.long_window} = ${fmt(calc.long_ma, 4)}`,
  ];

  return (
    <div className={`formula-box${compact ? " compact" : ""}`}>
      {lines.join("\n")}
      {"\n\n"}
      {t.strategyResult}:{" "}
      <span className={signalTone(strategy.signal)}>{strategy.signal || "-"}</span>
      {" · "}
      {strategy.reason || "-"}
    </div>
  );
}
