import { useEffect, useMemo, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import { KLINE_INTERVALS, useKlines } from "../hooks/useKlines";
import { fmt, fmtCompact } from "../utils";

const CHART_OPTIONS = {
  layout: {
    background: { color: "#0c1320" },
    textColor: "#8291a7",
    fontFamily: '"IBM Plex Mono", ui-monospace, monospace',
    fontSize: 11,
  },
  grid: {
    vertLines: { color: "rgba(83, 103, 134, 0.16)" },
    horzLines: { color: "rgba(83, 103, 134, 0.16)" },
  },
  crosshair: {
    vertLine: { color: "rgba(131, 151, 177, 0.45)", width: 1, style: 2 },
    horzLine: { color: "rgba(131, 151, 177, 0.45)", width: 1, style: 2 },
  },
  rightPriceScale: {
    borderColor: "rgba(74, 92, 119, 0.32)",
  },
  timeScale: {
    borderColor: "rgba(74, 92, 119, 0.32)",
    timeVisible: true,
    secondsVisible: false,
  },
};

function toUnixSeconds(timestamp) {
  return Math.floor(Date.parse(timestamp) / 1000);
}

function buildSeriesData(candles) {
  const candleData = [];
  const volumeData = [];
  const lookup = new Map();

  for (const candle of candles) {
    const time = toUnixSeconds(candle.timestamp);
    const up = candle.close >= candle.open;
    candleData.push({
      time,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    });
    volumeData.push({
      time,
      value: candle.volume,
      color: up ? "rgba(0, 192, 135, 0.45)" : "rgba(240, 82, 95, 0.45)",
    });
    lookup.set(time, candle);
  }

  return { candleData, volumeData, lookup };
}

function formatOhlcLine(candle, t) {
  if (!candle) {
    return null;
  }
  const change = candle.close - candle.open;
  const changePct = candle.open ? (change / candle.open) * 100 : 0;
  const tone = change >= 0 ? "up" : "down";
  const sign = change >= 0 ? "+" : "";

  return {
    tone,
    text: (
      <>
        <span>{t.openLabel} {fmt(candle.open, 2)}</span>
        <span>{t.highLabel} {fmt(candle.high, 2)}</span>
        <span>{t.lowLabel} {fmt(candle.low, 2)}</span>
        <span>{t.closeLabel} {fmt(candle.close, 2)}</span>
        <span className={tone}>
          {sign}
          {fmt(change, 2)} ({sign}
          {fmt(changePct, 2)}%)
        </span>
      </>
    ),
    volumeText: `${t.volume} ${fmtCompact(candle.volume, 3)}`,
  };
}

function applySeriesData(seriesRefs, candles) {
  if (!seriesRefs.candleSeries || !seriesRefs.volumeSeries) {
    return;
  }

  if (!candles.length) {
    seriesRefs.candleSeries.setData([]);
    seriesRefs.volumeSeries.setData([]);
    return;
  }

  const { candleData, volumeData } = buildSeriesData(candles);
  seriesRefs.candleSeries.setData(candleData);
  seriesRefs.volumeSeries.setData(volumeData);
  seriesRefs.chart?.timeScale().fitContent();
}

export default function CandlestickChart({ symbol, t, fallbackCandles = [], refreshMs = 60000 }) {
  const [period, setPeriod] = useState(() => {
    const saved = Number(localStorage.getItem("safetrade.kline.period"));
    return KLINE_INTERVALS.some((item) => item.period === saved) ? saved : 15;
  });
  const { candles, loading, error, usingFallback } = useKlines(period, 120, refreshMs, fallbackCandles);
  const [hoverCandle, setHoverCandle] = useState(null);

  const containerRef = useRef(null);
  const seriesRefs = useRef({
    chart: null,
    candleSeries: null,
    volumeSeries: null,
  });
  const lookupRef = useRef(new Map());

  const activeInterval = KLINE_INTERVALS.find((item) => item.period === period) || KLINE_INTERVALS[0];
  const displayInterval = usingFallback ? KLINE_INTERVALS.find((item) => item.period === 60) || activeInterval : activeInterval;
  const lastCandle = candles[candles.length - 1] || null;
  const displayCandle = hoverCandle || lastCandle;
  const ohlc = useMemo(() => formatOhlcLine(displayCandle, t), [displayCandle, t]);

  useEffect(() => {
    localStorage.setItem("safetrade.kline.period", String(period));
  }, [period]);

  useEffect(() => {
    lookupRef.current = buildSeriesData(candles).lookup;
  }, [candles]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return undefined;
    }

    const ensureChart = () => {
      if (seriesRefs.current.chart || container.clientWidth === 0 || container.clientHeight === 0) {
        return;
      }

      const chart = createChart(container, {
        ...CHART_OPTIONS,
        width: container.clientWidth,
        height: container.clientHeight,
      });
      const candleSeries = chart.addCandlestickSeries({
        upColor: "#00c087",
        downColor: "#f0525f",
        borderVisible: false,
        wickUpColor: "#00c087",
        wickDownColor: "#f0525f",
      });
      const volumeSeries = chart.addHistogramSeries({
        priceFormat: { type: "volume" },
        priceScaleId: "",
      });

      chart.priceScale("").applyOptions({
        scaleMargins: { top: 0.82, bottom: 0 },
      });
      candleSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.06, bottom: 0.24 },
      });

      seriesRefs.current = { chart, candleSeries, volumeSeries };

      chart.subscribeCrosshairMove((param) => {
        if (!param.time) {
          setHoverCandle(null);
          return;
        }
        setHoverCandle(lookupRef.current.get(param.time) || null);
      });
    };

    const resizeChart = () => {
      ensureChart();
      if (seriesRefs.current.chart) {
        seriesRefs.current.chart.applyOptions({
          width: container.clientWidth,
          height: container.clientHeight,
        });
      }
    };

    const resizeObserver = new ResizeObserver(resizeChart);
    resizeObserver.observe(container);
    resizeChart();

    return () => {
      resizeObserver.disconnect();
      seriesRefs.current.chart?.remove();
      seriesRefs.current = { chart: null, candleSeries: null, volumeSeries: null };
    };
  }, []);

  useEffect(() => {
    applySeriesData(seriesRefs.current, candles);
    setHoverCandle(null);
  }, [candles]);

  return (
    <div className="candlestick-panel">
      <div className="candlestick-toolbar">
        <div className="candlestick-intervals">
          {KLINE_INTERVALS.map((item) => (
            <button
              key={item.period}
              type="button"
              className={`interval-btn ${item.period === period ? "active" : ""}`}
              onClick={() => setPeriod(item.period)}
            >
              {item.label}
            </button>
          ))}
        </div>
        <span className="candlestick-brand">{t.tradingView}</span>
      </div>

      <div className="candlestick-meta">
        <div className="candlestick-symbol">
          {symbol} · {displayInterval.label}
        </div>
        <div className="candlestick-ohlc">{ohlc?.text}</div>
        <div className="candlestick-volume-label">{ohlc?.volumeText}</div>
      </div>

      {usingFallback ? <div className="candlestick-notice">{t.klineFallbackNotice}</div> : null}
      {error ? <div className="candlestick-error">{t.loadFailed}: {error}</div> : null}
      {loading && !candles.length ? <div className="candlestick-loading">{t.loadingChart}</div> : null}

      <div className="candlestick-chart" ref={containerRef} />
    </div>
  );
}
