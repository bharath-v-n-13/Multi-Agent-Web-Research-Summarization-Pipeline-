import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2, AlertCircle, Clock, RotateCcw } from "lucide-react";
import type { AgentStepProgress } from "../../types/research";

interface ProgressTimelineProps {
  steps: AgentStepProgress[];
  progressPercent: number;
  elapsedTime: number;
  status: "idle" | "running" | "completed" | "failed";
  iteration: number;
}

export const ProgressTimeline: React.FC<ProgressTimelineProps> = ({
  steps,
  progressPercent,
  elapsedTime,
  status,
  iteration,
}) => {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const getAgentHeader = (agent: string) => {
    switch (agent) {
      case "planner":
        return "Planner Agent Node";
      case "searcher":
        return "Searcher Agent Node (BM25 Index)";
      case "synthesizer":
        return "Synthesizer Agent Node (Gemini 2.5)";
      case "critic":
        return "Critic Agent Node (Self-Correction)";
      default:
        return "Agent Node";
    }
  };

  return (
    <div className="space-y-6 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-6 shadow-soft">
      {/* Telemetry Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-4 gap-4">
        <div className="space-y-1">
          <h2 className="text-base font-semibold text-slate-950 dark:text-slate-50 flex items-center gap-2">
            {status === "running" && <Loader2 className="h-4.5 w-4.5 animate-spin text-brand-navy dark:text-slate-300" />}
            {status === "completed" && <Check className="h-4.5 w-4.5 text-emerald-500" />}
            {status === "failed" && <AlertCircle className="h-4.5 w-4.5 text-rose-500" />}
            <span>Orchestration Execution</span>
          </h2>
          <p className="text-xs text-slate-400 font-medium">
            Workflow: Planner → Searcher → Synthesizer → Critic Loop
          </p>
        </div>

        {/* Clock & Timer */}
        <div className="flex items-center space-x-4 bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800/50 py-1.5 px-3 rounded-xl self-start sm:self-center font-mono">
          <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300">
            <Clock className="h-3.5 w-3.5 text-slate-400" />
            <span>ELAPSED: {formatTime(elapsedTime)}</span>
          </div>
          {iteration > 0 && (
            <div className="flex items-center space-x-1 text-xs font-semibold text-brand-teal dark:text-teal-400">
              <RotateCcw className="h-3.5 w-3.5 animate-spin" />
              <span>LOOP COUNT: {iteration}/2</span>
            </div>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs font-semibold text-slate-600 dark:text-slate-400">
          <span>Overall Workflow Progress</span>
          <span className="font-mono">{progressPercent}%</span>
        </div>
        <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: "0%" }}
            animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="h-full bg-brand-navy dark:bg-slate-100 rounded-full"
          />
        </div>
      </div>

      {/* Vertical Steps Timeline */}
      <div className="relative pl-8 space-y-6 pt-2">
        {/* Timeline bar */}
        <div className="absolute left-3.5 top-2 bottom-6 w-0.5 bg-slate-100 dark:bg-slate-800" />

        {steps.map((step) => {
          const isCurrent = step.status === "running";
          const isDone = step.status === "completed";
          const isFail = step.status === "failed";

          return (
            <div key={step.agent} className="relative group">
              {/* Timeline indicator circle */}
              <div className="absolute -left-8 top-1.5 flex h-7 w-7 items-center justify-center rounded-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                {isDone && (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400 animate-scaleIn">
                    <Check className="h-3 w-3" />
                  </div>
                )}
                {isCurrent && (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-brand-navy dark:bg-slate-100 text-white dark:text-brand-navy">
                    <Loader2 className="h-3 w-3 animate-spin" />
                  </div>
                )}
                {isFail && (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400 animate-scaleIn">
                    <AlertCircle className="h-3 w-3" />
                  </div>
                )}
                {step.status === "idle" && (
                  <div className="h-1.5 w-1.5 rounded-full bg-slate-300 dark:bg-slate-700" />
                )}
              </div>

              {/* Step Detail Card */}
              <div
                className={`rounded-xl border p-4 transition-all duration-300 ${
                  isCurrent
                    ? "border-slate-300 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-800/20 shadow-sm"
                    : isDone
                    ? "border-slate-100 dark:border-slate-800/40 opacity-70"
                    : isFail
                    ? "border-rose-200 dark:border-rose-950/20 bg-rose-50/10"
                    : "border-slate-100/50 dark:border-slate-900/50 opacity-40"
                }`}
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    {getAgentHeader(step.agent)}
                  </h3>
                  <AnimatePresence>
                    {isCurrent && step.iteration > 0 && (
                      <motion.span
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="rounded-full bg-brand-teal/10 dark:bg-teal-950/30 px-2 py-0.5 text-[10px] font-semibold text-brand-teal dark:text-teal-400 flex items-center space-x-1"
                      >
                        <RotateCcw className="h-2.5 w-2.5 animate-spin" />
                        <span>Loopback Run {step.iteration}</span>
                      </motion.span>
                    )}
                  </AnimatePresence>
                </div>
                
                {/* Step Action Logs */}
                <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-400">
                  {step.message}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Completion alert block */}
      {status === "completed" && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-emerald-50/40 dark:bg-emerald-950/10 border border-emerald-100 dark:border-emerald-950/25 p-4 text-center"
        >
          <span className="text-xs font-semibold text-emerald-800 dark:text-emerald-400">
            Autonomous research run compiled successfully. Redirecting to viewer...
          </span>
        </motion.div>
      )}
    </div>
  );
};
export default ProgressTimeline;
