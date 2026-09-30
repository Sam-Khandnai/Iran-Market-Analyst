import { Check } from "lucide-react";

const ORDER = ["data", "technical", "fundamental", "market_context", "news", "risk", "decision", "explanation"];

export function ProgressSteps({ completed, labels }: { completed: string[]; labels: Record<string, string> }) {
  return (
    <div className="progress-wrap">
      {ORDER.map((node) => {
        const isDone = completed.includes(node);
        const isActive = !isDone && completed.length === ORDER.indexOf(node);
        return (
          <div key={node} className={`progress-step ${isDone ? "done" : isActive ? "active" : ""}`}>
            {isDone ? <Check size={14} /> : isActive ? <span className="spinner" /> : <span style={{ width: 14 }} />}
            <span>{labels[node] ?? node}</span>
          </div>
        );
      })}
    </div>
  );
}
