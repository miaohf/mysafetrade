export function fmt(value, digits = 4) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "-";
  }
  return Number(value).toFixed(digits);
}

export function formatTimestamp(value) {
  return value.replace("T", " ").replace("+00:00", " UTC");
}

export function formatChartLabel(value) {
  return value.slice(5, 16).replace("T", " ");
}

export function signalTone(signal) {
  if (signal === "buy") return "buy";
  if (signal === "sell") return "sell";
  return "hold";
}
