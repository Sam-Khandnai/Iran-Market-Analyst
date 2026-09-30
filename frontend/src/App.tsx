import { useState } from "react";
import { SearchBar } from "./components/SearchBar";
import { PopularSymbols } from "./components/PopularSymbols";
import { ProgressSteps } from "./components/ProgressSteps";
import { ScoreCard, RiskCard } from "./components/ScoreCard";
import { SignalBadge } from "./components/SignalBadge";
import { AnalysisSummary } from "./components/AnalysisSummary";
import { EvidenceList } from "./components/EvidenceList";
import { PriceChart } from "./components/PriceChart";
import { AssetTabs, type ViewTab } from "./components/AssetTabs";
import { AssetGrid } from "./components/AssetGrid";
import { streamAnalysis } from "./api";
import type { AnalysisReport } from "./types";

export default function App() {
  const [tab, setTab] = useState<ViewTab>("stock");

  const [symbol, setSymbol] = useState("");
  const [loading, setLoading] = useState(false);
  const [completedNodes, setCompletedNodes] = useState<string[]>([]);
  const [labels, setLabels] = useState<Record<string, string>>({});
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (sym: string) => {
    setSymbol(sym);
    setLoading(true);
    setError(null);
    setReport(null);
    setCompletedNodes([]);

    try {
      for await (const evt of streamAnalysis(sym)) {
        if (evt.event === "node" && evt.node) {
          setCompletedNodes((prev) => [...prev, evt.node!]);
          if (evt.label) setLabels((prev) => ({ ...prev, [evt.node!]: evt.label! }));
          if (evt.report) setReport(evt.report);
        } else if (evt.event === "error") {
          setError(evt.message ?? "خطای ناشناخته");
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "ارتباط با سرور برقرار نشد");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="app-header">
        <h1>تحلیل‌گر هوشمند بورس ایران</h1>
        <p>تحلیل چندعاملی تکنیکال، بنیادی و ریسک بر پایه داده زنده TSETMC</p>
      </div>

      <AssetTabs active={tab} onChange={setTab} />

      {tab === "stock" && (
        <>
          <SearchBar
            value={symbol}
            onChange={setSymbol}
            onSubmit={() => runAnalysis(symbol)}
            loading={loading}
          />
          <PopularSymbols active={symbol} onSelect={(s) => !loading && runAnalysis(s)} />

          {error && <div className="error-box">{error}</div>}

          {loading && <ProgressSteps completed={completedNodes} labels={labels} />}

          {report && (
            <>
              <div className="score-grid">
                <ScoreCard label="تکنیکال" score={report.technical_analysis?.score ?? null} />
                <ScoreCard label="بنیادی" score={report.fundamental_analysis?.score ?? null} />
                <ScoreCard label="وضعیت بازار" score={report.market_context?.score ?? null} />
                <RiskCard level={report.risk_analysis?.risk_level ?? null} />
              </div>

              {report.decision && (
                <SignalBadge signal={report.decision.signal} confidence={report.decision.confidence} />
              )}

              <AnalysisSummary text={report.summary} />
              <EvidenceList factors={report.key_factors} risks={report.risks} />
              <PriceChart data={report.chart_data} />

              <div className="disclaimer">{report.disclaimer}</div>
            </>
          )}
        </>
      )}

      {tab === "gold_coin" && (
        <>
          <AssetGrid category="gold" />
          <div style={{ height: 20 }} />
          <AssetGrid category="coin" />
        </>
      )}

      {tab === "currency" && <AssetGrid category="currency" />}
    </div>
  );
}