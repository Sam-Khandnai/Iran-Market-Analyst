import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { AssetTrendResult, AssetHistoryPoint } from "../types";

const TREND_FA: Record<string, string> = { up: "صعودی", down: "نزولی", flat: "باثبات", unknown: "نامشخص" };

export function AssetChart({
  title, trend, history,
}: { title: string; trend: AssetTrendResult; history: AssetHistoryPoint[] }) {
  const trendColor = trend.trend === "up" ? "var(--green)" : trend.trend === "down" ? "var(--red)" : "var(--yellow)";

  return (
    <div className="section-card">
      <h3>{title} — روند {TREND_FA[trend.trend]}</h3>
      <div style={{ display: "flex", gap: 16, marginBottom: 12, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
        {trend.change_pct_1d !== null && <span>۱ روزه: {trend.change_pct_1d}٪</span>}
        {trend.change_pct_7d !== null && <span>۷ روزه: {trend.change_pct_7d}٪</span>}
        {trend.change_pct_30d !== null && <span>۳۰ روزه: {trend.change_pct_30d}٪</span>}
      </div>
      {history.length > 1 ? (
        <div style={{ direction: "ltr" }}>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={history}>
              <CartesianGrid stroke="#3a3a3a" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="trade_date" stroke="#9b9b9b" fontSize={10} tickLine={false} />
              <YAxis stroke="#9b9b9b" fontSize={10} tickLine={false} axisLine={false} domain={["auto", "auto"]} />
              <Tooltip contentStyle={{ background: "#2a2a2a", border: "1px solid #3a3a3a" }} />
              <Line type="monotone" dataKey="value" stroke={trendColor} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
          هنوز تاریخچه کافی برای رسم نمودار ثبت نشده؛ با گذر روزها نمودار تکمیل می‌شود.
        </p>
      )}
    </div>
  );
}
