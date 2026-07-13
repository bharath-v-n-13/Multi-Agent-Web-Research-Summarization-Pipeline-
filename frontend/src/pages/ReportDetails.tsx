import React from "react";
import { useParams, Link } from "react-router-dom";
import { useReport } from "../hooks/useResearch";
import ReportViewer from "../components/research/ReportViewer";
import { PageLoader } from "../components/common/Loader";
import EmptyState from "../components/common/EmptyState";
import { FileWarning, ChevronLeft } from "lucide-react";

export const ReportDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: report, isLoading, error } = useReport(id || "");

  if (isLoading) {
    return <PageLoader />;
  }

  if (error || !report) {
    return (
      <div className="space-y-6 max-w-xl mx-auto">
        <Link
          to="/reports"
          className="inline-flex items-center space-x-1 text-xs font-semibold text-slate-500 hover:text-slate-700 dark:hover:text-slate-350"
        >
          <ChevronLeft className="h-4 w-4" />
          <span>Back to History</span>
        </Link>
        <EmptyState
          icon={FileWarning}
          title="Report Not Found"
          description={
            error
              ? `An error occurred while loading this document: ${error.message}`
              : "The requested report UUID could not be located in your history log."
          }
          actionText="Return to History"
          onAction={() => (window.location.href = "/reports")}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Return button */}
      <Link
        to="/reports"
        className="inline-flex items-center space-x-1.5 text-xs font-bold text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 self-start"
      >
        <ChevronLeft className="h-4 w-4" />
        <span>Return to history</span>
      </Link>

      {/* Main Report Viewer content */}
      <ReportViewer report={report} />
    </div>
  );
};
export default ReportDetails;
