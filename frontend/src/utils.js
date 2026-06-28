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

export function parseSignedNumber(value) {
  if (value === null || value === undefined) {
    return null;
  }
  const normalized = String(value).replace("%", "").replace(",", "").trim();
  const num = Number(normalized);
  return Number.isNaN(num) ? null : num;
}

export function changeTone(value) {
  const num = parseSignedNumber(value);
  if (num === null || num === 0) {
    return "";
  }
  return num > 0 ? "up" : "down";
}

export function rsiTone(value) {
  const num = parseSignedNumber(value);
  if (num === null) {
    return "";
  }
  if (num >= 70) {
    return "warn";
  }
  if (num <= 30) {
    return "oversold";
  }
  return "";
}

export function maTrendTone(short, long) {
  const shortValue = parseSignedNumber(short);
  const longValue = parseSignedNumber(long);
  if (shortValue === null || longValue === null) {
    return "";
  }
  if (shortValue > longValue) {
    return "up";
  }
  if (shortValue < longValue) {
    return "down";
  }
  return "";
}

export function signalTone(signal) {
  if (signal === "buy") return "buy";
  if (signal === "sell") return "sell";
  return "hold";
}

export function sideTone(side) {
  const normalized = String(side || "").toLowerCase();
  if (normalized === "buy") {
    return "buy";
  }
  if (normalized === "sell") {
    return "sell";
  }
  return "";
}
