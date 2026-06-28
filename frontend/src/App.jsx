import { useEffect, useState } from "react";
import StatsGrid from "./components/StatsGrid";
import BotCyclePanel from "./components/BotCyclePanel";
import PriceChart from "./components/PriceChart";
import RsiChart from "./components/RsiChart";
import MaDetail from "./components/MaDetail";
import CandleTable from "./components/CandleTable";
import { useAnalysis } from "./hooks/useAnalysis";
import { template, translations } from "./i18n";

export default function App() {
  const { data, loading, error, updatedAt, reload } = useAnalysis(60000);
  const [language, setLanguage] = useState(() => localStorage.getItem("safetrade.language") || "zh");
  const t = translations[language] || translations.zh;

  useEffect(() => {
    localStorage.setItem("safetrade.language", language);
  }, [language]);

  if (loading && !data) {
    return <div className="app-shell app-shell--loading">{t.loading}</div>;
  }

  const meta = data?.meta || {};
  const points = data?.points || [];

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero-title">
          <h1>{t.appTitle}</h1>
          <p>{template(t.appSubtitle, { period: meta.kline_period || "-" })}</p>
        </div>
        <div className="toolbar">
          <span className="chip">
            <span className="chip-dot" />
            {t.autoRefresh}
          </span>
          {updatedAt ? (
            <span className="chip chip--time">{updatedAt.toLocaleString()}</span>
          ) : null}
          <button
            className="btn btn-sm"
            type="button"
            onClick={() => setLanguage((current) => (current === "zh" ? "en" : "zh"))}
          >
            {t.language}
          </button>
          <button className="btn btn-sm btn-primary" type="button" onClick={reload}>
            {t.refreshNow}
          </button>
        </div>
      </header>

      {error ? <div className="error-banner">{t.loadFailed}: {error}</div> : null}

      {data ? (
        <div className="dashboard">
          <StatsGrid data={data} t={t} />

          <section className="panel panel-bot">
            <div className="panel-header">
              <h2>{t.botLatestCycle}</h2>
            </div>
            <div className="panel-body panel-body--scroll">
              <BotCyclePanel botCycle={data.bot_cycle} t={t} compact />
            </div>
          </section>

          <section className="panel panel-price">
            <div className="panel-header">
              <h2>{t.priceAndMA}</h2>
              <span className="panel-caption">{t.priceCaption}</span>
            </div>
            <div className="panel-body">
              <PriceChart points={points} t={t} />
            </div>
          </section>

          <section className="panel panel-rsi">
            <div className="panel-header">
              <h2>RSI(14)</h2>
              <span className="panel-caption">{t.rsiCaption}</span>
            </div>
            <div className="panel-body">
              <RsiChart points={points} />
            </div>
          </section>

          <section className="panel panel-detail">
            <div className="panel-header">
              <h2>{t.maDetail}</h2>
            </div>
            <div className="panel-body panel-body--scroll">
              <MaDetail data={data} t={t} compact />
            </div>
          </section>

          <section className="panel panel-table">
            <div className="panel-header">
              <h2>{t.recentCandles}</h2>
              <span className="panel-caption">{t.recent12}</span>
            </div>
            <div className="panel-body panel-body--scroll">
              <CandleTable points={points} t={t} limit={12} compact />
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}
