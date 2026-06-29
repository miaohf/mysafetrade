import { useCallback, useEffect, useState } from "react";

export const KLINE_INTERVALS = [
  { label: "15m", period: 15 },
  { label: "1H", period: 60 },
  { label: "4H", period: 240 },
  { label: "1D", period: 1440 },
  { label: "1W", period: 10080 },
];

function normalizeCandles(raw) {
  return (raw || []).map((item) => ({
    timestamp: item.timestamp,
    open: item.open,
    high: item.high,
    low: item.low,
    close: item.close,
    volume: item.volume,
  }));
}

export function useKlines(period, limit = 120, refreshMs = 60000, fallbackCandles = []) {
  const [candles, setCandles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [usingFallback, setUsingFallback] = useState(false);

  const applyFallback = useCallback(() => {
    const normalized = normalizeCandles(fallbackCandles).slice(-limit);
    if (normalized.length) {
      setCandles(normalized);
      setUsingFallback(true);
      setError("");
      return true;
    }
    return false;
  }, [fallbackCandles, limit]);

  const load = useCallback(async () => {
    try {
      setError("");
      const response = await fetch(`/api/klines?period=${period}&limit=${limit}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      setCandles(normalizeCandles(payload.candles));
      setUsingFallback(false);
    } catch (err) {
      if (!applyFallback()) {
        setCandles([]);
        setUsingFallback(false);
        setError(err instanceof Error ? err.message : "load failed");
      }
    } finally {
      setLoading(false);
    }
  }, [period, limit, applyFallback]);

  useEffect(() => {
    setLoading(true);
    load();
    const timer = window.setInterval(load, refreshMs);
    return () => window.clearInterval(timer);
  }, [load, refreshMs]);

  return { candles, loading, error, usingFallback, reload: load };
}
