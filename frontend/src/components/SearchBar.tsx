import { Search, Loader2 } from "lucide-react";
import { FormEvent } from "react";

export function SearchBar({
  value, onChange, onSubmit, loading,
}: { value: string; onChange: (v: string) => void; onSubmit: () => void; loading: boolean }) {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (value.trim() && !loading) onSubmit();
  };
  return (
    <form className="search-row" onSubmit={handleSubmit}>
      <input
        className="search-input"
        placeholder="نماد را وارد کنید (مثلاً فولاد)"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={loading}
      />
      <button className="search-btn" type="submit" disabled={loading || !value.trim()}>
        {loading ? <Loader2 size={18} className="spinner-icon" /> : <Search size={18} />}
        {loading ? "در حال تحلیل..." : "تحلیل"}
      </button>
    </form>
  );
}
