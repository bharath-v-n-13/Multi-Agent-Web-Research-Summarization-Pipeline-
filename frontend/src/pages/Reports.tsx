import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useReports } from "../hooks/useResearch";
import { Search, FolderOpen, SlidersHorizontal, Calendar, Clock, Sparkles } from "lucide-react";
import EmptyState from "../components/common/EmptyState";
import { format, parseISO } from "date-fns";

export const Reports: React.FC = () => {
  const { data: reports = [] } = useReports();
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("newest");

  // Search filtering
  const filteredReports = reports.filter(
    (r) =>
      r.topic.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.summary.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Sorting
  const sortedReports = [...filteredReports].sort((a, b) => {
    if (sortBy === "newest") {
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    }
    if (sortBy === "oldest") {
      return new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime();
    }
    if (sortBy === "confidence") {
      return (b.critique?.confidence_score || 0) - (a.critique?.confidence_score || 0);
    }
    return 0;
  });

  const formatHistoryDate = (dateStr?: string) => {
    if (!dateStr) return "Recent compilation";
    try {
      return format(parseISO(dateStr), "MMM dd, yyyy 'at' hh:mm a");
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-slate-950 dark:text-slate-50">
            Research History Logs
          </h1>
          <p className="text-sm text-slate-500 font-medium">
            Review and download previously compiled multi-agent reports.
          </p>
        </div>
      </div>

      {/* Search & Sort Panel */}
      <div className="flex flex-col sm:flex-row items-center gap-4 bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800/80 p-4 rounded-2xl shadow-soft w-full">
        {/* Search */}
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4.5 w-4.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search reports by topic name or summary keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-850 rounded-xl py-2 pl-10 pr-4 text-sm outline-none focus:border-brand-navy dark:focus:border-slate-600 text-slate-900 dark:text-slate-100 placeholder:text-slate-400"
          />
        </div>

        {/* Sort dropdown */}
        <div className="flex items-center space-x-2 shrink-0 w-full sm:w-auto">
          <SlidersHorizontal className="h-4.5 w-4.5 text-slate-400 hidden sm:inline" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="w-full sm:w-auto bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-850 rounded-xl px-3 py-2 text-sm outline-none cursor-pointer text-slate-700 dark:text-slate-300 font-semibold"
          >
            <option value="newest">Sort: Newest First</option>
            <option value="oldest">Sort: Oldest First</option>
            <option value="confidence">Sort: Confidence Rating</option>
          </select>
        </div>
      </div>

      {/* Reports Grid List */}
      {sortedReports.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedReports.map((report) => {
            const confidencePercent = Math.round(report.critique.confidence_score * 100);
            return (
              <div
                key={report.report_id}
                className="flex flex-col justify-between rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft hover:shadow-premium hover:border-slate-300 dark:hover:border-slate-700 transition-all duration-300 group"
              >
                <div className="space-y-4">
                  {/* Metadata Tag */}
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium font-mono">
                    <span className="flex items-center space-x-1">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>{formatHistoryDate(report.created_at)}</span>
                    </span>
                  </div>

                  {/* Topic & Summary */}
                  <div className="space-y-2">
                    <h3 className="text-sm font-bold text-slate-950 dark:text-slate-50 group-hover:text-brand-teal dark:group-hover:text-teal-400 transition-colors line-clamp-2">
                      {report.topic}
                    </h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-3 leading-relaxed">
                      {report.summary}
                    </p>
                  </div>
                </div>

                {/* Footer specs */}
                <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <div className="flex items-center space-x-3 text-xs font-mono">
                    <span
                      className="inline-flex items-center rounded-md bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-800/80 px-2 py-0.5 font-bold text-[10px] text-slate-500"
                      title="Run Time"
                    >
                      <Clock className="h-3 w-3 mr-1" />
                      {report.metadata.wall_clock_seconds}s
                    </span>
                    <span
                      className="inline-flex items-center rounded-md bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-950/10 px-2 py-0.5 font-bold text-[10px] text-emerald-600 dark:text-emerald-400"
                      title="Confidence Score"
                    >
                      <Sparkles className="h-3 w-3 mr-1" />
                      {confidencePercent}%
                    </span>
                  </div>

                  <Link
                    to={`/reports/${report.report_id}`}
                    className="text-xs font-bold text-slate-900 dark:text-slate-200 group-hover:text-brand-teal dark:group-hover:text-teal-400 hover:underline"
                  >
                    View report →
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState
          icon={FolderOpen}
          title="No Reports Found"
          description={
            searchQuery
              ? `No logs match your search for "${searchQuery}".`
              : "No historical research runs found in your client environment."
          }
          actionText={searchQuery ? undefined : "Launch New Research"}
          onAction={searchQuery ? undefined : () => (window.location.href = "/research")}
        />
      )}
    </div>
  );
};
export default Reports;
