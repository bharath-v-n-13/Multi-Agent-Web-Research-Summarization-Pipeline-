import React from "react";
import { ExternalLink, Link2, Calendar } from "lucide-react";
import type { ReportSource } from "../../types/research";
import { format } from "date-fns";

interface SourceCardProps {
  source: ReportSource;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  const getDomain = (url: string) => {
    try {
      return new URL(url).hostname;
    } catch {
      return "academic-portal.org";
    }
  };

  const formatScrapedDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), "MMM d, yyyy HH:mm");
    } catch {
      return dateStr;
    }
  };

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block rounded-xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-4 hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-soft transition-all duration-200"
    >
      <div className="flex items-start justify-between gap-3">
        {/* Source info */}
        <div className="space-y-1">
          <span className="inline-flex items-center rounded-md bg-slate-100 dark:bg-slate-800 px-2 py-0.5 text-[10px] font-bold font-mono text-slate-600 dark:text-slate-400">
            {source.source_id}
          </span>
          <h4 className="text-sm font-semibold text-slate-950 dark:text-slate-50 group-hover:text-brand-teal dark:group-hover:text-teal-400 transition-colors line-clamp-1">
            {source.title}
          </h4>
          <div className="flex items-center space-x-1.5 text-xs text-slate-400">
            <Link2 className="h-3.5 w-3.5" />
            <span className="line-clamp-1">{getDomain(source.url)}</span>
          </div>
        </div>

        {/* Relevance Score meter */}
        <div className="text-right">
          <span className="text-[10px] font-semibold text-slate-400 block">RELEVANCE</span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 font-mono">
            {source.relevance_score.toFixed(4)}
          </span>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[10px] text-slate-400 font-medium">
        <span className="flex items-center space-x-1">
          <Calendar className="h-3.5 w-3.5" />
          <span>Scraped: {formatScrapedDate(source.scraped_at)}</span>
        </span>
        <span className="inline-flex items-center text-slate-500 group-hover:translate-x-0.5 transition-transform">
          <span className="mr-1">Open link</span>
          <ExternalLink className="h-3 w-3" />
        </span>
      </div>
    </a>
  );
};
export default SourceCard;
