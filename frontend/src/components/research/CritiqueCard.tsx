import React from "react";
import { Shield, ShieldAlert, AlertTriangle, HelpCircle } from "lucide-react";
import type { ReportCritique } from "../../types/research";

interface CritiqueCardProps {
  critique: ReportCritique;
}

export const CritiqueCard: React.FC<CritiqueCardProps> = ({ critique }) => {
  const scorePercent = Math.round(critique.confidence_score * 100);

  const getScoreProgressColor = (score: number) => {
    if (score >= 0.85) return "bg-emerald-500";
    if (score >= 0.7) return "bg-amber-500";
    return "bg-rose-500";
  };

  return (
    <div className="space-y-6 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-6 shadow-soft">
      {/* Title */}
      <div className="flex items-center space-x-2 border-b border-slate-100 dark:border-slate-800 pb-4">
        <Shield className="h-5 w-5 text-brand-navy dark:text-slate-300" />
        <h3 className="text-base font-semibold text-slate-950 dark:text-slate-50">
          Agent Self-Critique & Assessment
        </h3>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Confidence Gauge */}
        <div className="flex flex-col items-center justify-center p-4 border border-slate-100 dark:border-slate-800/80 rounded-xl bg-slate-50/30 dark:bg-slate-900/50">
          <span className="text-xs font-semibold text-slate-400">CONFIDENCE LEVEL</span>
          <div className="relative mt-4 flex items-center justify-center">
            {/* Simple circular gauge */}
            <div className="h-24 w-24 rounded-full border-4 border-slate-100 dark:border-slate-800 flex flex-col items-center justify-center">
              <span className="text-2xl font-black text-slate-800 dark:text-slate-100 font-mono">
                {scorePercent}%
              </span>
              <span className="text-[9px] font-bold text-slate-400">STABILITY</span>
            </div>
          </div>
          {/* Horizontal progress representation */}
          <div className="w-full mt-4 space-y-1">
            <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full ${getScoreProgressColor(critique.confidence_score)}`}
                style={{ width: `${scorePercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* Knowledge Gaps */}
        <div className="p-4 border border-slate-100 dark:border-slate-800/80 rounded-xl bg-slate-50/30 dark:bg-slate-900/50 space-y-3">
          <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center space-x-1.5 uppercase tracking-wide">
            <HelpCircle className="h-4 w-4 text-slate-400" />
            <span>Omissions & Gaps</span>
          </h4>
          <div className="space-y-1.5 max-h-[110px] overflow-y-auto pr-1">
            {critique.gaps.length > 0 ? (
              critique.gaps.map((gap, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 p-2 text-[11px] font-medium text-slate-600 dark:text-slate-400"
                >
                  • {gap}
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 italic">No omissions flagged in research coverage.</p>
            )}
          </div>
        </div>

        {/* Bias Warnings */}
        <div className="p-4 border border-slate-100 dark:border-slate-800/80 rounded-xl bg-slate-50/30 dark:bg-slate-900/50 space-y-3">
          <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 flex items-center space-x-1.5 uppercase tracking-wide">
            <ShieldAlert className="h-4 w-4 text-slate-400" />
            <span>Bias & Balance Flags</span>
          </h4>
          <div className="space-y-1.5 max-h-[110px] overflow-y-auto pr-1">
            {critique.bias_flags.length > 0 ? (
              critique.bias_flags.map((bias, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-rose-100 dark:border-rose-950/20 bg-rose-50/10 dark:bg-rose-950/5 p-2 text-[11px] font-medium text-rose-700 dark:text-rose-400 flex items-start space-x-1.5"
                >
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-rose-500" />
                  <span>{bias}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 italic">No skew or bias indicators flagged in texts.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default CritiqueCard;
