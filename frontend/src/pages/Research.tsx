import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useResearch } from "../hooks/useResearch";
import { useProgress } from "../hooks/useProgress";
import ResearchForm from "../components/research/ResearchForm";
import ProgressTimeline from "../components/research/ProgressTimeline";
import { toast } from "sonner";
import type { ResearchRequest } from "../types/research";
import { AlertCircle } from "lucide-react";
import Button from "../components/common/Button";

export const Research: React.FC = () => {
  const navigate = useNavigate();
  const [showProgress, setShowProgress] = useState<boolean>(false);
  const [lastRequest, setLastRequest] = useState<ResearchRequest | null>(null);

  const { runResearch, isProcessing, error, report } = useResearch();

  const isSuccess = !!report;
  const isError = !!error;

  const { steps, progressPercent, elapsedTime, status, iteration } =
    useProgress(isProcessing, isSuccess, isError);

  const handleFormSubmit = async (values: ResearchRequest) => {
    setLastRequest(values);
    setShowProgress(true);
    toast.info("Research request submitted. Initializing agents...");

    try {
      const result = await runResearch(values);
      toast.success("Research completed successfully.");
      
      // Auto-navigate to report details after a short 2-second delay to show completion state
      setTimeout(() => {
        navigate(`/reports/${result.report_id}`);
      }, 2500);
    } catch (err) {
      toast.error("Research failed. See details below.");
    }
  };

  const handleRetry = () => {
    if (lastRequest) {
      handleFormSubmit(lastRequest);
    }
  };

  const handleCancel = () => {
    setShowProgress(false);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fadeIn">
      <div className="space-y-1">
        <h1 className="text-xl md:text-2xl font-bold tracking-tight text-slate-950 dark:text-slate-50">
          Autonomous Research Lab
        </h1>
        <p className="text-sm text-slate-500">
          Start a new AI-powered research loop across pre-crawled websites.
        </p>
      </div>

      {!showProgress && (
        <ResearchForm onSubmit={handleFormSubmit} isLoading={isProcessing} />
      )}

      {showProgress && (
        <div className="space-y-6">
          {/* Progress Visual Tracker */}
          <ProgressTimeline
            steps={steps}
            progressPercent={progressPercent}
            elapsedTime={elapsedTime}
            status={status}
            iteration={iteration}
          />

          {/* Action Buttons based on status */}
          {status === "failed" && (
            <div className="rounded-2xl border border-rose-200 dark:border-rose-950/20 bg-rose-50/10 p-5 space-y-4">
              <div className="flex items-start space-x-3 text-xs text-rose-800 dark:text-rose-400">
                <AlertCircle className="h-4.5 w-4.5 shrink-0 text-rose-500" />
                <div className="space-y-1">
                  <p className="font-semibold">Research Loop Interrupted</p>
                  <p className="text-rose-600 dark:text-rose-400/80">
                    {error?.message || "Connection to FastAPI backend timed out or failed."}
                  </p>
                </div>
              </div>
              <div className="flex space-x-3">
                <Button variant="primary" size="sm" onClick={handleRetry}>
                  Retry Compile
                </Button>
                <Button variant="outline" size="sm" onClick={handleCancel}>
                  Adjust Form Settings
                </Button>
              </div>
            </div>
          )}

          {status === "running" && (
            <div className="text-center">
              <p className="text-[11px] font-medium text-slate-400 italic">
                Please remain on this page. Research loops typically require 8-20 seconds to compile.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
export default Research;
