"use client";
import { useState } from "react";

type Row = {
  agency_slug: string;
  Title: string;
  Level_Name: string;
  Level: string | number;
  Date: string;
  Value: number;
};

function SimpleBarChart({ data }: { data: Row[] }) {
  if (!data || data.length === 0) return <div>No data for chart</div>;

  const COLORS = ["#4f46e5", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4", "#a855f7", "#3b82f6"];

  const dates = Array.from(new Set(data.map((r) => r.Date.slice(0, 10)))).sort();
  const agencies = Array.from(new Set(data.map((r) => r.agency_slug))).sort();

  const totalsByDate: Record<string, Record<string, number>> = {};
  dates.forEach((d) => {
    totalsByDate[d] = {};
    agencies.forEach((a) => {
      totalsByDate[d][a] = 0;
    });
  });

  data.forEach((r) => {
    const d = r.Date.slice(0, 10);
    const a = r.agency_slug;
    totalsByDate[d][a] = (totalsByDate[d][a] || 0) + Number(r.Value || 0);
  });

  const maxTotal = Math.max(
    ...dates.map((d) => agencies.reduce((sum, a) => sum + (totalsByDate[d][a] || 0), 0)),
    1,
  );

  const chartWidth = Math.max(dates.length * 50, 200);
  const barWidth = 26;

  return (
    <div className="space-y-3">
      <svg width="100%" height={200} viewBox={`0 0 ${chartWidth} 200`}>
        {dates.map((date, idx) => {
          const x = idx * 50 + 12;
          let currentY = 170;
          return (
            <g key={date}>
              {agencies.map((agency, ai) => {
                const val = totalsByDate[date][agency] || 0;
                const h = (val / maxTotal) * 130;
                currentY -= h;
                return (
                  <rect
                    key={`${date}-${agency}`}
                    x={x}
                    y={currentY}
                    width={barWidth}
                    height={h}
                    fill={COLORS[ai % COLORS.length]}
                  />
                );
              })}
              <text x={x - 2} y={188} fontSize={10} fill="#374151" transform={`rotate(-35 ${x} 188)`}>
                {date}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="flex flex-wrap gap-3 text-xs text-gray-700">
        {agencies.map((agency, idx) => (
          <span key={agency} className="flex items-center gap-2">
            <span className="inline-block h-3 w-3 rounded-sm" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
            {agency}
          </span>
        ))}
      </div>
    </div>
  );
}

const METRIC_OPTIONS = [
  "Word count",
  "Keyword count",
  "cross-references Average",
  "Lexical diversity",
  "Citation depth",
];

const LEVEL_NAMES = ["Title", "Chapter", "Subchapter", "Part", "Subpart", "Section"];

export default function EcfrMetricsClient() {
  const [metricName, setMetricName] = useState(METRIC_OPTIONS[0]);
  const [levelName, setLevelName] = useState(LEVEL_NAMES[1]);
  const [startDt, setStartDt] = useState("2022-01-01");
  const [endDt, setEndDt] = useState("2022-02-01");
  const [agencies, setAgencies] = useState("BIA");
  const [rows, setRows] = useState<Row[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"table" | "graph">("table");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  async function fetchData(e?: React.FormEvent) {
    e?.preventDefault();
    setLoading(true);
    try {
      const levelIndex = LEVEL_NAMES.indexOf(levelName);
      const res = await fetch(
        `http://localhost:8000/metric_json?metric_name=${encodeURIComponent(metricName)}&level=${levelIndex}&start_dt=${startDt}&end_dt=${endDt}&agencies=${encodeURIComponent(
          agencies,
        )}`,
        { cache: "no-store" },
      );
      // const res = await fetch(
      //   `http://localhost:8000/metric_json?metric_id=${metricId}&level=${level}&start_dt=${startDt}&end_dt=${endDt}`,
      //   { cache: "no-store" },
      // );
      const data = await res.json();
      setRows(data);
    } catch (err) {
      console.error(err);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={fetchData} className="flex gap-2 items-end">
        <div>
          <label className="block text-sm">Metric</label>
          <select value={metricName} onChange={(e) => setMetricName(e.target.value)} className="border px-2 py-1">
            {METRIC_OPTIONS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm">Level</label>
          <select value={levelName} onChange={(e) => setLevelName(e.target.value)} className="border px-2 py-1">
            {LEVEL_NAMES.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm">Start</label>
          <input type="date" value={startDt} onChange={(e) => setStartDt(e.target.value)} className="border px-2 py-1" />
        </div>
        <div>
          <label className="block text-sm">End</label>
          <input type="date" value={endDt} onChange={(e) => setEndDt(e.target.value)} className="border px-2 py-1" />
        </div>
        <div>
          <label className="block text-sm">Agencies (comma-separated)</label>
          <input
            type="text"
            value={agencies}
            onChange={(e) => setAgencies(e.target.value)}
            className="border px-2 py-1"
            placeholder="BIA,NSF"
          />
        </div>
        <div>
          <button className="btn-primary px-3 py-1" type="submit" disabled={loading}>
            {loading ? "Loading…" : "Fetch"}
          </button>
        </div>
      </form>

      {rows && rows.length > 0 && (
        <div>
          <div className="flex space-x-2 mb-4">
            <button
              type="button"
              className={`px-3 py-1 rounded ${activeTab === "table" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-700"}`}
              onClick={() => setActiveTab("table")}
            >
              Table
            </button>
            <button
              type="button"
              className={`px-3 py-1 rounded ${activeTab === "graph" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-700"}`}
              onClick={() => setActiveTab("graph")}
            >
              Graph
            </button>
          </div>

          {activeTab === "table" && (
            <div className="rounded border p-3">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left">
                    <th>Agency</th>
                    <th>Title</th>
                    <th>Level</th>
                    <th>Date</th>
                    <th
                      className="text-right cursor-pointer select-none"
                      onClick={() => setSortDirection((s) => (s === "asc" ? "desc" : "asc"))}
                      aria-sort={sortDirection === "asc" ? "ascending" : "descending"}
                    >
                      Value {sortDirection === "asc" ? "▲" : "▼"}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {(() => {
                    const sorted = rows ? [...rows] : [];
                    sorted.sort((a, b) => {
                      const av = Number(a.Value || 0);
                      const bv = Number(b.Value || 0);
                      return sortDirection === "asc" ? av - bv : bv - av;
                    });
                    return sorted.map((r, i) => (
                      <tr key={i} className="border-t">
                        <td>{r.agency_slug}</td>
                        <td>{r.Title}</td>
                        <td>{r.Level}</td>
                        <td>{new Date(r.Date).toLocaleDateString()}</td>
                        <td className="text-right">{r.Value}</td>
                      </tr>
                    ));
                  })()}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === "graph" && (
            <div className="rounded border p-3">
              <h4 className="mb-2">Metric over time</h4>
              <SimpleBarChart data={rows} />
            </div>
          )}
        </div>
      )}

      {rows && rows.length === 0 && <div>No results.</div>}
    </div>
  );
}
