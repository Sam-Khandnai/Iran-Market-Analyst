function colorFor(score: number): string {
  if (score >= 65) return "var(--green)";
  if (score <= 35) return "var(--red)";
  return "var(--yellow)";
}

export function ScoreCard({ label, score }: { label: string; score: number | null }) {
  const value = score ?? 0;
  return (
    <div className="score-card">
      <div className="label">{label}</div>
      <div className="value" style={{ color: colorFor(value) }}>
        {score !== null ? Math.round(value) : "—"}
        <span style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}> /100</span>
      </div>
      <div className="score-bar">
        <div className="score-bar-fill" style={{ width: `${value}%`, background: colorFor(value) }} />
      </div>
    </div>
  );
}

export function RiskCard({ level }: { level: string | null }) {
  const map: Record<string, { color: string; text: string }> = {
    low: { color: "var(--green)", text: "کم" },
    medium: { color: "var(--yellow)", text: "متوسط" },
    high: { color: "var(--red)", text: "بالا" },
  };
  const info = level ? map[level] ?? { color: "var(--text-secondary)", text: level } : { color: "var(--text-secondary)", text: "—" };
  return (
    <div className="score-card">
      <div className="label">ریسک</div>
      <div className="value" style={{ color: info.color }}>{info.text}</div>
    </div>
  );
}
