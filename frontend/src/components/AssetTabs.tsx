import { TrendingUp, Coins, DollarSign } from "lucide-react";

export type ViewTab = "stock" | "gold_coin" | "currency";

const TABS: { id: ViewTab; label: string; icon: React.ReactNode }[] = [
  { id: "stock", label: "بورس", icon: <TrendingUp size={15} /> },
  { id: "gold_coin", label: "طلا و سکه", icon: <Coins size={15} /> },
  { id: "currency", label: "ارز", icon: <DollarSign size={15} /> },
];

export function AssetTabs({ active, onChange }: { active: ViewTab; onChange: (t: ViewTab) => void }) {
  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
      {TABS.map((t) => (
        <button
          key={t.id}
          className={`chip ${active === t.id ? "active" : ""}`}
          style={{ display: "flex", alignItems: "center", gap: 6 }}
          onClick={() => onChange(t.id)}
        >
          {t.icon} {t.label}
        </button>
      ))}
    </div>
  );
}
