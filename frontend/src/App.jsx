import StatsGrid from "./components/StatsGrid";
import PriceChart from "./components/PriceChart";
import RsiChart from "./components/RsiChart";
import MaDetail from "./components/MaDetail";
import CandleTable from "./components/CandleTable";
import { useAnalysis } from "./hooks/useAnalysis";

export default function App() {
  const { data, loading, error, updatedAt, reload } = useAnalysis(60000);

  if (loading && !data) {
    return <div className="app-shell loading">正在加载 PRL/USDT 行情...</div>;
  }

  const meta = data?.meta || {};
  const points = data?.points || [];

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <h1>PRL/USDT 分析看板</h1>
          <p>
            SafeTrade 公开 API · {meta.kline_period} 分钟 K 线 · 与机器人策略同源计算
          </p>
        </div>
        <div className="toolbar">
          <span className="chip">
            <span className="chip-dot" />
            自动刷新 60 秒
          </span>
          {updatedAt ? (
            <span className="chip">更新于 {updatedAt.toLocaleString()}</span>
          ) : null}
          <button className="btn btn-primary" type="button" onClick={reload}>
            立即刷新
          </button>
        </div>
      </header>

      {error ? <div className="error-banner">加载失败: {error}</div> : null}

      {data ? (
        <>
          <StatsGrid data={data} />

          <section className="panel">
            <div className="panel-header">
              <h2>价格与均线</h2>
              <span className="panel-caption">收盘价 · MA7 · MA25</span>
            </div>
            <PriceChart points={points} />
          </section>

          <section className="panel">
            <div className="panel-header">
              <h2>RSI(14)</h2>
              <span className="panel-caption">虚线: 30 / 70</span>
            </div>
            <RsiChart points={points} />
          </section>

          <section className="panel">
            <div className="panel-header">
              <h2>MA7 / MA25 计算明细</h2>
            </div>
            <MaDetail data={data} />
          </section>

          <section className="panel">
            <div className="panel-header">
              <h2>最近 K 线</h2>
              <span className="panel-caption">最近 12 根</span>
            </div>
            <CandleTable points={points} />
          </section>
        </>
      ) : null}
    </div>
  );
}
