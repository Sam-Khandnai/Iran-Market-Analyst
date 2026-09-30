export type Signal =
  | "STRONG_POSITIVE" | "POSITIVE" | "WATCH"
  | "NEUTRAL" | "NEGATIVE" | "STRONG_NEGATIVE";

export interface ChartPoint {
  date: string;
  close: number;
  sma20: number | null;
  sma50: number | null;
  volume: number;
}

export interface AnalysisReport {
  symbol: string;
  technical_analysis: Record<string, any>;
  fundamental_analysis: Record<string, any>;
  market_context: Record<string, any>;
  news_analysis: Record<string, any>;
  risk_analysis: Record<string, any>;
  decision: { signal: Signal; confidence: number } | null;
  key_factors: string[];
  risks: string[];
  evidence: { source: string; description: string; value: any }[];
  summary: string;
  disclaimer: string;
  generated_at: string;
  chart_data: ChartPoint[];
}

export interface StreamEvent {
  event: "node" | "done" | "error";
  node?: string;
  label?: string;
  report?: AnalysisReport;
  message?: string;
}

export const POPULAR_SYMBOLS = [
  "فولاد", "فملی", "وبملت", "شپنا", "خودرو",
  "فارس", "شستا", "پارسان", "وبصادر", "کگل",
  "رمپنا", "تاپیکو", "شبندر", "اخابر",
] as const;

export type AssetCategory = "currency" | "gold" | "coin";

export interface AssetQuote {
  key: string;
  title: string;
  category: AssetCategory;
  unit: string;
  value: number;
  change: number;
  fetched_at: string;
}

export interface AssetHistoryPoint {
  trade_date: string;
  value: number;
}

export interface AssetTrendResult {
  key: string;
  as_of: string;
  current_value: number;
  change_1d: number | null;
  change_pct_1d: number | null;
  change_pct_7d: number | null;
  change_pct_30d: number | null;
  trend: "up" | "down" | "flat" | "unknown";
  data_points: number;
}

export interface AssetAnalysisReport {
  key: string;
  title: string;
  category: string;
  unit: string;
  trend: AssetTrendResult;
  signal: {
    key: string;
    score: number;
    signal: Signal;
    confidence: number;
    volatility_pct: number | null;
    momentum_pct: number | null;
    factors: string[];
  };
  summary: string;
  history: AssetHistoryPoint[];
  disclaimer: string;
}
export const POPULAR_ASSETS: Record<"gold" | "coin" | "currency", { key: string; label: string }[]> = {
  gold: [
    { key: "bub_18ayar", label: "طلای ۱۸ عیار" },
    { key: "usd_xau", label: "انس جهانی (دلار)" },
  ],
  coin: [
    { key: "bub_sekkeh", label: "سکه امامی" },
    { key: "bub_bahar", label: "سکه بهار آزادی" },
    { key: "bub_nim", label: "نیم سکه" },
    { key: "bub_rob", label: "ربع سکه" },
    { key: "bub_gerami", label: "سکه گرمی" },
  ],
  currency: [
    { key: "usd", label: "دلار آمریکا" },
    { key: "eur", label: "یورو" },
    { key: "aed", label: "درهم امارات" },
  ],
};