import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ChevronDown, ChevronRight, FileText, Globe, Shield, Activity, Calendar } from "lucide-react";
import type { ResearchReportResponse } from "../../types/research";
import SourceCard from "./SourceCard";
import CritiqueCard from "./CritiqueCard";
import DownloadButtons from "./DownloadButtons";
import { format } from "date-fns";

interface ReportViewerProps {
  report: ResearchReportResponse;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ report }) => {
  const [activeTab, setActiveTab] = useState<string>("summary");
  const [expandedSections, setExpandedSections] = useState<Record<number, boolean>>({ 0: true });

  const toggleSection = (idx: number) => {
    setExpandedSections((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const navItems = [
    { id: "summary", name: "Executive Summary", icon: FileText },
    { id: "sections", name: "Research Details", icon: Activity },
    { id: "sources", name: "References & Sources", icon: Globe },
    { id: "critique", name: "Quality Critique", icon: Shield },
  ];

  const formatReportDate = (dateStr?: string) => {
    if (!dateStr) return "Just compiled";
    try {
      return format(new Date(dateStr), "MMMM d, yyyy 'at' h:mm a");
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Control Block */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div className="space-y-1">
          <h1 className="text-xl md:text-2xl font-bold tracking-tight text-slate-950 dark:text-slate-50">
            {report.topic}
          </h1>
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <Calendar className="h-3.5 w-3.5" />
            <span>Compiled on: {formatReportDate(report.created_at)}</span>
          </div>
        </div>
        <div className="self-start md:self-center">
          <DownloadButtons report={report} />
        </div>
      </div>

      {/* Main split grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Side Navigation Links */}
        <div className="lg:col-span-1">
          <nav className="sticky top-20 space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  const el = document.getElementById(item.id);
                  if (el) {
                    el.scrollIntoView({ behavior: "smooth", block: "start" });
                  }
                }}
                className={`flex w-full items-center space-x-3 rounded-lg px-3 py-2 text-xs font-semibold tracking-wide uppercase transition-all ${
                  activeTab === item.id
                    ? "bg-slate-100 dark:bg-slate-800 text-brand-navy dark:text-slate-100"
                    : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900/50 hover:text-slate-800 dark:hover:text-slate-200"
                }`}
              >
                <item.icon className="h-4.5 w-4.5 shrink-0 text-slate-400" />
                <span>{item.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Right Side Content Viewer */}
        <div className="lg:col-span-3 space-y-10">
          {/* Executive Summary */}
          <section id="summary" className="scroll-mt-20 space-y-4">
            <h2 className="text-base font-bold uppercase tracking-wider text-slate-950 dark:text-slate-50 border-b border-slate-100 dark:border-slate-800 pb-2">
              Executive Summary
            </h2>
            <div className="prose dark:prose-invert max-w-none text-sm leading-relaxed text-slate-600 dark:text-slate-300">
              <ReactMarkdown>{report.summary}</ReactMarkdown>
            </div>
          </section>

          {/* Research Sections */}
          <section id="sections" className="scroll-mt-20 space-y-6">
            <h2 className="text-base font-bold uppercase tracking-wider text-slate-950 dark:text-slate-50 border-b border-slate-100 dark:border-slate-800 pb-2">
              Research Details
            </h2>
            <div className="space-y-4">
              {report.sections.map((sec, idx) => {
                const isExpanded = expandedSections[idx] !== false;
                return (
                  <div
                    key={idx}
                    className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 overflow-hidden shadow-sm"
                  >
                    {/* Expandable Section Accordion Header */}
                    <button
                      onClick={() => toggleSection(idx)}
                      className="flex w-full items-center justify-between px-5 py-4 bg-slate-50/50 dark:bg-slate-900/50 hover:bg-slate-100/50 dark:hover:bg-slate-850/50 border-b border-slate-100 dark:border-slate-850 transition-colors"
                    >
                      <span className="text-sm font-bold text-slate-950 dark:text-slate-100">
                        {sec.heading}
                      </span>
                      {isExpanded ? (
                        <ChevronDown className="h-4.5 w-4.5 text-slate-400" />
                      ) : (
                        <ChevronRight className="h-4.5 w-4.5 text-slate-400" />
                      )}
                    </button>

                    {/* Section body */}
                    {isExpanded && (
                      <div className="p-5 space-y-4">
                        <div className="prose dark:prose-invert max-w-none text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                          <ReactMarkdown>{sec.content}</ReactMarkdown>
                        </div>

                        {/* citations */}
                        {sec.citations.length > 0 && (
                          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60 flex flex-wrap gap-2 items-center">
                            <span className="text-[10px] font-bold text-slate-400 uppercase mr-1">Citations:</span>
                            {sec.citations.map((cite, cidx) => {
                              // Cross reference URL to find matching source_id
                              const matchingSrc = report.sources.find((s) => s.url === cite);
                              const citationLabel = matchingSrc ? matchingSrc.source_id : `Source ${cidx+1}`;
                              return (
                                <a
                                  key={cidx}
                                  href={cite}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center rounded-md bg-brand-navy/5 dark:bg-white/5 border border-brand-navy/10 dark:border-white/10 px-2 py-0.5 text-[10px] font-semibold text-brand-navy dark:text-slate-300 hover:bg-brand-navy/10 dark:hover:bg-white/10 transition-colors"
                                  title={cite}
                                >
                                  {citationLabel}
                                </a>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>

          {/* References & Sources */}
          <section id="sources" className="scroll-mt-20 space-y-4">
            <h2 className="text-base font-bold uppercase tracking-wider text-slate-950 dark:text-slate-50 border-b border-slate-100 dark:border-slate-800 pb-2">
              References and Sources
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {report.sources.map((source) => (
                <SourceCard key={source.source_id} source={source} />
              ))}
            </div>
          </section>

          {/* Quality Critique */}
          <section id="critique" className="scroll-mt-20">
            <CritiqueCard critique={report.critique} />
          </section>

          {/* System Telemetry Metadata */}
          <section className="rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-5 shadow-soft space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wide">
              Research Telemetry
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
              <div className="p-3 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/50 rounded-xl">
                <span className="text-[10px] font-semibold text-slate-400 block">ELAPSED TIME</span>
                <span className="text-base font-bold text-slate-800 dark:text-slate-200">
                  {report.metadata.wall_clock_seconds}s
                </span>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/50 rounded-xl">
                <span className="text-[10px] font-semibold text-slate-400 block">SOURCES VISITED</span>
                <span className="text-base font-bold text-slate-800 dark:text-slate-200">
                  {report.metadata.total_urls_visited}
                </span>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/50 rounded-xl">
                <span className="text-[10px] font-semibold text-slate-400 block">GRAPH CYCLES</span>
                <span className="text-base font-bold text-slate-800 dark:text-slate-200">
                  {report.metadata.agent_interactions}
                </span>
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800/50 rounded-xl">
                <span className="text-[10px] font-semibold text-slate-400 block">CONFIDENCE INDEX</span>
                <span className="text-base font-bold text-slate-800 dark:text-slate-200">
                  {report.critique.confidence_score.toFixed(2)}
                </span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};
export default ReportViewer;
