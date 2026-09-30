import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";

export function AnalysisSummary({ text }: { text: string }) {
  const [shown, setShown] = useState("");

  useEffect(() => {
    setShown("");
    if (!text) return;
    let i = 0;
    const interval = setInterval(() => {
      i += 3;
      setShown(text.slice(0, i));
      if (i >= text.length) clearInterval(interval);
    }, 12);
    return () => clearInterval(interval);
  }, [text]);

  return (
    <div className="section-card">
      <h3><Sparkles size={16} color="var(--accent)" /> تحلیل هوشمند</h3>
      <p className={shown.length < text.length ? "cursor-blink" : ""}>{shown}</p>
    </div>
  );
}
