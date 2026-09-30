import type {
  StreamEvent,
  AssetQuote,
  AssetTrendResult,
  AssetHistoryPoint,
  AssetAnalysisReport,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ---------- تحلیل سهام بورس (streaming) ----------

export async function* streamAnalysis(
  symbol: string,
  timeframe = "daily",
  analysisPeriod = "1y",
): AsyncGenerator<StreamEvent> {
  const res = await fetch(`${BASE_URL}/v1/analyze/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, timeframe, analysis_period: analysisPeriod }),
  });

  if (!res.ok || !res.body) {
    let message = `خطای شبکه: ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData?.detail) message = String(errorData.detail);
    } catch {
      // نادیده گرفته می‌شود
    }
    throw new Error(message);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const event of events) {
      const trimmed = event.trim();
      if (!trimmed.startsWith("data:")) continue;
      const jsonStr = trimmed.slice(5).trim();
      if (!jsonStr) continue;
      try {
        yield JSON.parse(jsonStr) as StreamEvent;
      } catch {
        // پیام ناقص SSE؛ نادیده گرفته می‌شود
      }
    }
  }
}

// ---------- طلا / سکه / ارز ----------

export async function fetchPopularAssets(): Promise<AssetQuote[]> {
  const res = await fetch(`${BASE_URL}/v1/assets/popular`);
  if (!res.ok) {
    throw new Error(`خطای دریافت دارایی‌ها: ${res.status}`);
  }
  return res.json();
}

export async function fetchAssetTrend(
  key: string,
): Promise<{ trend: AssetTrendResult; history: AssetHistoryPoint[] }> {
  const res = await fetch(`${BASE_URL}/v1/assets/${key}/trend`);
  if (!res.ok) {
    throw new Error(`خطای دریافت روند: ${res.status}`);
  }
  return res.json();
}

export async function fetchAssetAnalysis(key: string): Promise<AssetAnalysisReport> {
  const res = await fetch(`${BASE_URL}/v1/assets/${key}/analyze`);

  if (!res.ok) {
    let message = `خطای تحلیل دارایی: ${res.status}`;
    try {
      const errorData = await res.json();
      if (errorData?.detail) message = String(errorData.detail);
    } catch {
      // نادیده گرفته می‌شود
    }
    throw new Error(message);
  }

  return res.json();
}