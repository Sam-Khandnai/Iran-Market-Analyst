import { ListChecks, AlertTriangle } from "lucide-react";

export function EvidenceList({ factors, risks }: { factors: string[]; risks: string[] }) {
  if (factors.length === 0 && risks.length === 0) return null;
  return (
    <div className="section-card">
      <h3><ListChecks size={16} color="var(--green)" /> شواهد و منابع</h3>
      <div className="pill-list" style={{ marginBottom: risks.length ? 12 : 0 }}>
        {factors.map((f, i) => (
          <span key={i} className="pill factor">{f}</span>
        ))}
      </div>
      {risks.length > 0 && (
        <>
          <h3 style={{ marginTop: 4 }}><AlertTriangle size={16} color="var(--red)" /> ریسک‌های شناسایی‌شده</h3>
          <div className="pill-list">
            {risks.map((r, i) => (
              <span key={i} className="pill risk">{r}</span>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
