import { useState } from "react";
import { Search, Loader2 } from "lucide-react";
import { fetchAssetAnalysis } from "../api";
import { POPULAR_ASSETS, type AssetAnalysisReport } from "../types";
import { AssetAnalysisView } from "./AssetAnalysisView";

export function AssetGrid({ category }: { category: "gold" | "coin" | "currency" }) {
  const items = POPULAR_ASSETS[category];
  const [selectedKey, setSelectedKey] = useState<string>(items[0]?.key ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<AssetAnalysisReport | null>(null);

  const runAnalysis = async (key: string) => {
    setSelectedKey(key);
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await fetchAssetAnalysis(key);
      setReport(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "خطا در تحلیل");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="search-row">
        <select
          className="search-input"
          value={selectedKey}
          onChange={(e) => setSelectedKey(e.target.value)}
          disabled={loading}
        >
          {items.map((i) => (
            <option key={i.key} value={i.key}>{i.label}</option>
          ))}
        </select>
        <button
          className="search-btn"
          disabled={loading || !selectedKey}
          onClick={() => runAnalysis(selectedKey)}
        >
          {loading ? <Loader2 size={18} className="spinner-icon" /> : <Search size={18} />}
          {loading ? "در حال تحلیل..." : "تحلیل"}
        </button>
      </div>

      <div className="popular-row">
        {items.map((i) => (
          <button
            key={i.key}
            className={`chip ${selectedKey === i.key ? "active" : ""}`}
            onClick={() => !loading && runAnalysis(i.key)}
          >
            {i.label}
          </button>
        ))}
      </div>

      {error && <div className="error-box">{error}</div>}
      {loading && <div className="progress-wrap">در حال دریافت و تحلیل داده...</div>}
      {report && <AssetAnalysisView report={report} />}
    </>
  );
}
