import React from "react";
import { Link } from "react-router-dom";
import { useReports } from "../hooks/useResearch";
import {
  TrendingUp,
  FileText,
  Compass,
  Zap,
  Activity,
  PlusCircle,
  FolderOpen,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { format, parseISO } from "date-fns";

const MOCK_CHARTS_DATA = [
  { date: "Jul 08", runs: 2, confidence: 88, sources: 12, time: 7.2 },
  { date: "Jul 09", runs: 5, confidence: 91, sources: 24, time: 8.6 },
  { date: "Jul 10", runs: 3, confidence: 89, sources: 18, time: 6.9 },
  { date: "Jul 11", runs: 8, confidence: 93, sources: 38, time: 9.1 },
  { date: "Jul 12", runs: 4, confidence: 90, sources: 20, time: 8.2 },
  { date: "Jul 13", runs: 6, confidence: 92, sources: 32, time: 7.8 },
];

export const Dashboard: React.FC = () => {
  const { data: reports = [] } = useReports();

  // Compute analytics
  const totalReports = reports.length;
  
  const totalSources = reports.reduce(
    (acc, cur) => acc + (cur.sources?.length || 0),
    0
  );
  
  const avgConfidence = totalReports
    ? Math.round(
        (reports.reduce((acc, cur) => acc + (cur.critique?.confidence_score || 0), 0) /
          totalReports) *
          100
      )
    : 0;

  const avgRuntime = totalReports
    ? (
        reports.reduce((acc, cur) => acc + (cur.metadata?.wall_clock_seconds || 0), 0) /
        totalReports
      ).toFixed(1)
    : "0.0";

  // Build chart statistics from actual history, falling back to mock if empty
  const chartData = totalReports
    ? reports
        .slice()
        .reverse()
        .map((r) => {
          let dateStr = "Recent";
          if (r.created_at) {
            try {
              dateStr = format(parseISO(r.created_at), "MMM dd");
            } catch {
              dateStr = "Recent";
            }
          }
          return {
            date: dateStr,
            runs: 1,
            confidence: Math.round(r.critique.confidence_score * 100),
            sources: r.sources.length,
            time: r.metadata.wall_clock_seconds,
            topic: r.topic,
          };
        })
    : MOCK_CHARTS_DATA;

  const recentReports = reports.slice(0, 3);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-slate-900 dark:bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 text-white shadow-premium">
        <div className="space-y-2 max-w-lg">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight">
            Welcome to the AI Research Lab
          </h1>
          <p className="text-sm text-slate-300 leading-relaxed">
            Configure topic inputs and monitor multi-agent graph workflows executing BM25 queries, HTML scraping, and critical self-evaluations.
          </p>
        </div>
        <Link to="/research" className="self-start md:self-center shrink-0">
          <button className="flex items-center space-x-2 rounded-xl bg-white text-slate-950 px-5 py-2.5 text-sm font-semibold tracking-wide hover:bg-slate-100 transition-all shadow-sm">
            <PlusCircle className="h-4.5 w-4.5" />
            <span>Launch Research Run</span>
          </button>
        </Link>
      </div>

      {/* Analytics Widgets Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Reports */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
              Total Runs
            </span>
            <FileText className="h-4.5 w-4.5 text-slate-400" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-slate-900 dark:text-slate-50 font-mono">
              {totalReports}
            </h3>
            <p className="text-[10px] font-semibold text-slate-400 mt-1">RESEARCH COMPILATIONS</p>
          </div>
        </div>

        {/* Total Sources */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
              Sources Cached
            </span>
            <Compass className="h-4.5 w-4.5 text-slate-400" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-slate-900 dark:text-slate-50 font-mono">
              {totalSources}
            </h3>
            <p className="text-[10px] font-semibold text-slate-400 mt-1">UNIQUE WEBPAGE MATCHES</p>
          </div>
        </div>

        {/* Average Confidence */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
              Avg Stability
            </span>
            <TrendingUp className="h-4.5 w-4.5 text-slate-400" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-slate-900 dark:text-slate-50 font-mono">
              {avgConfidence}%
            </h3>
            <p className="text-[10px] font-semibold text-slate-400 mt-1">CRITIC COVERAGE RATING</p>
          </div>
        </div>

        {/* Average Runtime */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">
              Avg Runtime
            </span>
            <Zap className="h-4.5 w-4.5 text-slate-400" />
          </div>
          <div>
            <h3 className="text-2xl font-black text-slate-900 dark:text-slate-50 font-mono">
              {avgRuntime}s
            </h3>
            <p className="text-[10px] font-semibold text-slate-400 mt-1">WALL-CLOCK DURATION</p>
          </div>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Research Confidence Trend */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
            <Activity className="h-4 w-4" />
            <span>Confidence Index Trends (%)</span>
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorConfidence" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#008080" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#008080" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={10} tickLine={false} />
                <YAxis domain={[50, 100]} stroke="#94A3B8" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(15, 23, 42, 0.95)",
                    border: "none",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "11px",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="confidence"
                  stroke="#008080"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorConfidence)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Runtime Performance */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-4">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
            <Zap className="h-4 w-4" />
            <span>Execution Duration per Run (Seconds)</span>
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={10} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={10} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(15, 23, 42, 0.95)",
                    border: "none",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "11px",
                  }}
                />
                <Bar dataKey="time" fill="#002B49" radius={[4, 4, 0, 0]} maxBarSize={35} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent compilations */}
      <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center space-x-2">
            <FolderOpen className="h-4 w-4" />
            <span>Recent Research Reports</span>
          </h3>
          <Link to="/reports" className="text-xs font-semibold text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            View All
          </Link>
        </div>

        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {recentReports.length > 0 ? (
            recentReports.map((report) => (
              <div key={report.report_id} className="py-3.5 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                <div className="space-y-1">
                  <Link
                    to={`/reports/${report.report_id}`}
                    className="text-sm font-bold text-slate-900 dark:text-slate-100 hover:text-brand-teal dark:hover:text-teal-400 transition-colors"
                  >
                    {report.topic}
                  </Link>
                  <p className="text-xs text-slate-400 line-clamp-1 max-w-xl">
                    {report.summary}
                  </p>
                </div>
                <div className="flex items-center space-x-4 shrink-0 font-mono text-xs">
                  <span className="rounded bg-slate-50 dark:bg-slate-800 px-2 py-0.5 text-slate-500 font-semibold">
                    {report.metadata.wall_clock_seconds}s
                  </span>
                  <span className="rounded bg-emerald-50 dark:bg-emerald-950/20 px-2 py-0.5 text-emerald-600 dark:text-emerald-400 font-semibold">
                    {Math.round(report.critique.confidence_score * 100)}%
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-6 text-xs text-slate-400 italic">
              No reports compiled yet. Launch a new run to get started.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
