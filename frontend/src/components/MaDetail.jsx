import { fmt, fmtCompact, signalTone } from "../utils";
import { template } from "../i18n";

function CheckRow({ label, actual, threshold, pass, t }) {
  return (
    <tr>
      <td>{label}</td>
      <td>{actual}</td>
      <td>{threshold}</td>
      <td className={pass ? "up" : "down"}>{pass ? t.pass : t.fail}</td>
    </tr>
  );
}

function CloseGrid({ values, columns = 5 }) {
  if (!values?.length) {
    return null;
  }
  return (
    <div className="close-grid" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
      {values.map((value, index) => (
        <span key={`${value}-${index}`} className="close-cell">
          {value.toFixed(4)}
        </span>
      ))}
    </div>
  );
}

export default function MaDetail({ data, t, compact = false }) {
  const calc = data.ma_calculation || {};
  const strategy = data.strategy || {};
  const latest = data.latest || {};
  const volume = data.volume_analysis || {};
  const micro = data.microstructure_analysis || {};

  const rsiPass = latest.rsi14 == null || latest.rsi14 <= strategy.max_buy_rsi;

  return (
    <div className={`ma-detail${compact ? " compact" : ""}`}>
      <section className="ma-detail-section">
        <div className="ma-detail-title">MA7</div>
        <CloseGrid values={calc.short_closes} columns={7} />
        <div className="ma-detail-formula">
          MA7 = {calc.short_sum?.toFixed(4)} / {calc.short_window} = {fmt(calc.short_ma, 4)}
        </div>
      </section>

      <section className="ma-detail-section">
        <div className="ma-detail-title">MA25</div>
        <CloseGrid values={calc.long_closes} columns={5} />
        <div className="ma-detail-formula">
          {template(t.ma25Formula, { window: calc.long_window })} = {calc.long_sum?.toFixed(4)} / {calc.long_window} ={" "}
          {fmt(calc.long_ma, 4)}
        </div>
      </section>

      <section className="ma-detail-section">
        <div className="ma-detail-title">{t.volumeFilters}</div>
        <table className="compact check-table">
          <thead>
            <tr>
              <th>{t.filterItem}</th>
              <th>{t.actualValue}</th>
              <th>{t.threshold}</th>
              <th>{t.status}</th>
            </tr>
          </thead>
          <tbody>
            <CheckRow
              label={t.volumeRatio}
              actual={volume.volume_ratio == null ? "-" : `${fmt(volume.volume_ratio, 2)}x`}
              threshold={`>= ${fmt(volume.min_volume_ratio, 2)}x`}
              pass={volume.volume_confirmed}
              t={t}
            />
            <CheckRow
              label={t.quoteVolume}
              actual={fmtCompact(volume.latest_quote_volume, 2)}
              threshold={`>= ${fmt(volume.min_quote_volume, 0)}`}
              pass={volume.quote_volume_confirmed}
              t={t}
            />
            <CheckRow
              label="RSI14"
              actual={fmt(latest.rsi14, 2)}
              threshold={`<= ${fmt(strategy.max_buy_rsi, 0)}`}
              pass={rsiPass}
              t={t}
            />
          </tbody>
        </table>
      </section>

      <section className="ma-detail-section">
        <div className="ma-detail-title">{t.microFilters}</div>
        <table className="compact check-table">
          <thead>
            <tr>
              <th>{t.filterItem}</th>
              <th>{t.actualValue}</th>
              <th>{t.threshold}</th>
              <th>{t.status}</th>
            </tr>
          </thead>
          <tbody>
            <CheckRow
              label={t.spread}
              actual={micro.spread_pct == null ? "-" : `${fmt(micro.spread_pct, 2)}%`}
              threshold={`<= ${fmt(micro.max_spread_pct, 1)}%`}
              pass={micro.spread_confirmed}
              t={t}
            />
            <CheckRow
              label={t.askBidRatio}
              actual={fmt(micro.ask_bid_ratio, 2)}
              threshold={`<= ${fmt(micro.max_ask_bid_ratio, 2)}`}
              pass={micro.depth_confirmed}
              t={t}
            />
            <CheckRow
              label={t.buyPressure}
              actual={micro.buy_quote_ratio == null ? "-" : `${(micro.buy_quote_ratio * 100).toFixed(0)}%`}
              threshold={`>= ${(micro.min_buy_trade_ratio * 100).toFixed(0)}%`}
              pass={micro.buy_pressure_confirmed}
              t={t}
            />
          </tbody>
        </table>
      </section>

      <section className="ma-detail-section ma-detail-result">
        {t.strategyResult}:{" "}
        <span className={signalTone(strategy.signal)}>{strategy.signal || "-"}</span>
        {" · "}
        {t.rawSignal}:{" "}
        <span className={signalTone(strategy.raw_signal)}>{strategy.raw_signal || "-"}</span>
        <div className="ma-detail-reason">{strategy.reason || "-"}</div>
      </section>
    </div>
  );
}
