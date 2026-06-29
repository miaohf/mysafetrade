import { useEffect, useState } from "react";
import MarketActivityPanel from "./components/MarketActivityPanel";
import StatsGrid from "./components/StatsGrid";
import BotCyclePanel from "./components/BotCyclePanel";
import CandlestickChart from "./components/CandlestickChart";
import MaPriceChart from "./components/MaPriceChart";
import RsiChart from "./components/RsiChart";
import MaDetail from "./components/MaDetail";
import TickerSummary from "./components/TickerSummary";
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
        <div className="hero-top">
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
        </div>
        {data ? <StatsGrid data={data} t={t} /> : null}
      </header>

      {error ? <div className="error-banner">{t.loadFailed}: {error}</div> : null}

      {data ? (
        <div className="dashboard">
          <div className="dashboard-side dashboard-side--left">
            <section className="panel panel-market">
              <div className="panel-header">
                <h2>{t.marketDepth}</h2>
              </div>
              <div className="panel-body panel-body--fill">
                <MarketActivityPanel data={data} t={t} />
              </div>
            </section>

            <section className="panel panel-table">
              <div className="panel-header">
                <h2>{t.recentCandles}</h2>
                <span className="panel-caption">{t.recent8}</span>
              </div>
              <div className="panel-body panel-body--scroll">
                <CandleTable points={points} t={t} limit={8} compact />
              </div>
            </section>
          </div>

          <section className="panel panel-price">
            <div className="panel-header">
              <h2>{t.candlestickChart}</h2>
            </div>
            <div className="panel-body panel-body--chart">
              <CandlestickChart symbol={meta.symbol || "PRL/USDT"} t={t} fallbackCandles={points} />
            </div>
          </section>

          <section className="panel panel-bot">
            <div className="panel-header">
              <h2>{t.botLatestCycle}</h2>
            </div>
            <div className="panel-body panel-body--fill panel-body--stack">
              <div className="panel-body--scroll bot-panel-scroll">
                <BotCyclePanel botCycle={data.bot_cycle} t={t} compact />
              </div>
              <TickerSummary ticker={data.ticker} microstructure={data.microstructure_analysis} t={t} />
            </div>
          </section>

          <section className="panel panel-signals">
            <div className="signal-stack">
              <div className="signal-block">
                <div className="signal-header">
                  <h2>{t.priceAndMA}</h2>
                  <span className="panel-caption">{t.priceCaption}</span>
                </div>
                <div className="signal-body">
                  <MaPriceChart points={points} t={t} />
                </div>
              </div>
              <div className="signal-block">
                <div className="signal-header">
                  <h2>RSI(14)</h2>
                  <span className="panel-caption">{t.rsiCaption}</span>
                </div>
                <div className="signal-body">
                  <RsiChart points={points} />
                </div>
              </div>
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

        </div>
      ) : null}
    </div>
  );
}
