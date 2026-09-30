import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { LineChart as ChartIcon } from "lucide-react";

interface ChartPoint {
  date: string;
  close: number;
  sma20: number | null;
  sma50: number | null;
  volume: number;
}

function formatDate(d: string) {
  const parts = d.split("-");
  return `${parts[1]}/${parts[2]}`;
}

function DarkTooltip({ active, payload, label }: any) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div style={{
      background: "#2a2a2a", border: "1px solid #3a3a3a", borderRadius: 8,
      padding: "8px 12px", fontSize: "0.78rem", direction: "ltr",
    }}>
      <div style={{ color: "#9b9b9b", marginBottom: 4 }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.dataKey} style={{ color: p.color }}>
          {p.name}: {p.value?.toLocaleString?.() ?? p.value}
        </div>
      ))}
    </div>
  );
}

export function PriceChart({ data }: { data: ChartPoint[] }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="section-card">
      <h3><ChartIcon size={16} color="var(--blue)" /> نمودار قیمت و میانگین متحرک</h3>
      <div style={{ direction: "ltr" }}>
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
            <CartesianGrid stroke="#3a3a3a" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="date" tickFormatter={formatDate}
              stroke="#9b9b9b" fontSize={11} tickLine={false} axisLine={{ stroke: "#3a3a3a" }}
              minTickGap={30}
            />
            <YAxis
              yAxisId="price" orientation="right" stroke="#9b9b9b" fontSize={11}
              tickLine={false} axisLine={false} domain={["auto", "auto"]}
            />
            <YAxis yAxisId="volume" orientation="left" hide domain={[0, "dataMax * 4"]} />
            <Tooltip content={<DarkTooltip />} />
            <Legend wrapperStyle={{ fontSize: "0.78rem", color: "#9b9b9b" }} />
            <Bar yAxisId="volume" dataKey="volume" name="حجم" fill="#3a3a3a" opacity={0.6} barSize={3} />
            <Line
              yAxisId="price" type="monotone" dataKey="close" name="قیمت پایانی"
              stroke="#d97757" strokeWidth={2} dot={false}
            />
            <Line
              yAxisId="price" type="monotone" dataKey="sma20" name="میانگین ۲۰ روزه"
              stroke="#60a5fa" strokeWidth={1.5} dot={false} strokeDasharray="4 2"
            />
            <Line
              yAxisId="price" type="monotone" dataKey="sma50" name="میانگین ۵۰ روزه"
              stroke="#4ade80" strokeWidth={1.5} dot={false} strokeDasharray="4 2"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
