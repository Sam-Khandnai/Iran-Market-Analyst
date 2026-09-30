import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Sparkles, ListChecks } from "lucide-react";
import { SignalBadge } from "./SignalBadge";
import type { AssetAnalysisReport } from "../types";

function formatDate(d: string) {
  const p = d.split("-");
  return `${p[1]}/${p[2]}`;
}

export function AssetAnalysisView({ report }: { report: AssetAnalysisReport }) {
  const s = report.signal;
  return (
    <div className="section-card">
      <h3>{report.title}</h3>

      <div className="score-grid" style={{ marginTop: 12 }}>
        <div className="score-card">
          <div className="label">امتیاز روند</div>
          <div className="value" style={{ color: s.score >= 65 ? "var(--green)" : s.score <= 35 ? "var(--red)" : "var(--yellow)" }}>
            {Math.round(s.score)}
          </div>
        </div>
        <div className="score-card">
          <div className="label">مومنتوم</div>
          <div className="value" style={{ fontSize: "1.1rem" }}>
            {s.momentum_pct !== null ? `${s.momentum_pct > 0 ? "+" : ""}${s.momentum_pct}%` : "—"}
          </div>
        </div>
        <div className="score-card">
          <div className="label">نوسان‌پذیری</div>
          <div className="value" style={{ fontSize: "1.1rem" }}>
            {s.volatility_pct !== null ? `${s.volatility_pct}%` : "—"}
          </div>
        </div>
      </div>

      <SignalBadge signal={s.signal} confidence={s.confidence} />

      <div className="section-card" style={{ marginTop: 0 }}>
        <h3><Sparkles size={16} color="var(--accent)" /> تحلیل</h3>
        <p>{report.summary}</p>
      </div>

      {s.factors.length > 0 && (
        <div className="section-card">
          <h3><ListChecks size={16} color="var(--green)" /> شواهد</h3>
          <div className="pill-list">
            {s.factors.map((f, i) => (
              <span key={i} className={`pill ${f.includes("negative") || f.includes("high_volatility") ? "risk" : "factor"}`}>
                {f}
              </span>
            ))}
          </div>
        </div>
      )}

      {report.history.length > 1 ? (
        <div style={{ direction: "ltr" }}>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={report.history}>
              <CartesianGrid stroke="#3a3a3a" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="trade_date" tickFormatter={formatDate} stroke="#9b9b9b" fontSize={10} tickLine={false} />
              <YAxis stroke="#9b9b9b" fontSize={10} tickLine={false} axisLine={false} domain={["auto", "auto"]} />
              <Tooltip contentStyle={{ background: "#2a2a2a", border: "1px solid #3a3a3a" }} />
              <Line type="monotone" dataKey="value" stroke="var(--accent)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
          هنوز تاریخچه کافی ثبت نشده؛ با گذر روزها نمودار کامل‌تر می‌شود.
        </p>
      )}

      <div className="disclaimer">{report.disclaimer}</div>
    </div>
  );
}

