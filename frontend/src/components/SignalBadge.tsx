const SIGNAL_MAP: Record<string, { text: string; bg: string; fg: string }> = {
  STRONG_POSITIVE: { text: "سیگنال قوی مثبت", bg: "rgba(74,222,128,0.15)", fg: "var(--green)" },
  POSITIVE:        { text: "مثبت",           bg: "rgba(74,222,128,0.1)", fg: "var(--green)" },
  WATCH:           { text: "در حال رصد",     bg: "rgba(250,204,21,0.12)", fg: "var(--yellow)" },
  NEUTRAL:         { text: "خنثی",           bg: "rgba(155,155,155,0.15)", fg: "var(--text-secondary)" },
  NEGATIVE:        { text: "منفی",           bg: "rgba(248,113,113,0.1)", fg: "var(--red)" },
  STRONG_NEGATIVE: { text: "سیگنال قوی منفی", bg: "rgba(248,113,113,0.15)", fg: "var(--red)" },
};

export function SignalBadge({ signal, confidence }: { signal: string; confidence: number }) {
  const info = SIGNAL_MAP[signal] ?? SIGNAL_MAP.NEUTRAL;
  return (
    <div className="decision-panel">
      <span className="signal-badge" style={{ background: info.bg, color: info.fg }}>
        {info.text}
      </span>
      <span className="confidence-text">سطح اطمینان: {Math.round(confidence * 100)}٪</span>
    </div>
  );
}
