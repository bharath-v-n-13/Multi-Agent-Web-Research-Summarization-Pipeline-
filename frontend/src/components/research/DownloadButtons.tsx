import React from "react";
import { Download, FileDown, Code } from "lucide-react";
import Button from "../common/Button";
import { apiService } from "../../services/api";
import type { ResearchReportResponse } from "../../types/research";
import { toast } from "sonner";

interface DownloadButtonsProps {
  report: ResearchReportResponse;
}

export const DownloadButtons: React.FC<DownloadButtonsProps> = ({ report }) => {
  const handleDownload = (format: "markdown" | "json" | "pdf") => {
    try {
      apiService.downloadReportFile(report, format);
      toast.success(`Successfully initiated ${format.toUpperCase()} download.`);
    } catch (err) {
      toast.error(`Failed to download report as ${format.toUpperCase()}.`);
    }
  };

  return (
    <div className="flex flex-wrap gap-3">
      {/* Markdown Download */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleDownload("markdown")}
        className="text-xs font-semibold py-1.5 flex items-center space-x-1.5"
      >
        <FileDown className="h-4.5 w-4.5 text-slate-400" />
        <span>Download Markdown</span>
      </Button>

      {/* JSON Download */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => handleDownload("json")}
        className="text-xs font-semibold py-1.5 flex items-center space-x-1.5"
      >
        <Code className="h-4.5 w-4.5 text-slate-400" />
        <span>Download JSON</span>
      </Button>

      {/* PDF Download */}
      <Button
        variant="primary"
        size="sm"
        onClick={() => handleDownload("pdf")}
        className="text-xs font-semibold py-1.5 flex items-center space-x-1.5"
      >
        <Download className="h-4.5 w-4.5" />
        <span>Export PDF Report</span>
      </Button>
    </div>
  );
};
export default DownloadButtons;
