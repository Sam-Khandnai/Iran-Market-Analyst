import { POPULAR_SYMBOLS } from "../types";

export function PopularSymbols({
  active, onSelect,
}: { active: string; onSelect: (s: string) => void }) {
  return (
    <div className="popular-row">
      {POPULAR_SYMBOLS.map((sym) => (
        <button
          key={sym}
          className={`chip ${active === sym ? "active" : ""}`}
          onClick={() => onSelect(sym)}
        >
          {sym}
        </button>
      ))}
    </div>
  );
}
