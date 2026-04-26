import { useState, useEffect } from "react";
import { getAnalytics } from "../api";
import KPICard from "../components/KPICard";
import TimeSeriesChart from "../components/TimeSeriesChart";
import CategoryBarChart from "../components/CategoryBarChart";
import AgentLeaderboard from "../components/AgentLeaderboard";

const WINDOWS = ["today", "week", "month", "all"];

export default function AnalyticsPage() {
  const [window, setWindow] = useState("week");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    getAnalytics(window)
      .then(setData)
      .catch((err) => setError(err.response?.data?.detail || "Failed to load analytics"))
      .finally(() => setLoading(false));
  }, [window]);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">Analytics</h1>
        <div className="flex gap-1 bg-slate-100 rounded-lg p-1">
          {WINDOWS.map((w) => (
            <button
              key={w}
              onClick={() => setWindow(w)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                window === w
                  ? "bg-white text-slate-800 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              }`}
            >
              {w === "all" ? "All time" : w.charAt(0).toUpperCase() + w.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-6 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : data ? (
        <>
          {/* KPI cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <KPICard
              label="Total Tickets"
              value={data.kpis.total_tickets}
              color="indigo"
            />
            <KPICard
              label="Avg Turnaround"
              value={`${data.kpis.avg_tat_hours}h`}
              sub="time to resolve"
              color="slate"
            />
            <KPICard
              label="SLA Breaches"
              value={data.kpis.sla_breach_count}
              sub={`${data.kpis.sla_breach_rate}% of resolved`}
              color={data.kpis.sla_breach_rate > 20 ? "red" : "green"}
            />
            <KPICard
              label="Draft Approval Rate"
              value={`${data.kpis.draft_approval_rate}%`}
              sub="approved without edit"
              color={data.kpis.draft_approval_rate >= 70 ? "green" : "amber"}
            />
            <KPICard
              label="Avg AI Confidence"
              value={`${(data.kpis.avg_classification_confidence * 100).toFixed(1)}%`}
              color="indigo"
            />
            <KPICard
              label="Avg Edit Distance"
              value={data.kpis.avg_edit_distance.toFixed(3)}
              sub="0 = no edits, 1 = full rewrite"
              color={data.kpis.avg_edit_distance < 0.2 ? "green" : "amber"}
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            <TimeSeriesChart data={data.time_series} />
            <CategoryBarChart data={data.category_breakdown} />
          </div>

          {/* Leaderboard */}
          <AgentLeaderboard data={data.agent_leaderboard} />
        </>
      ) : null}
    </div>
  );
}
