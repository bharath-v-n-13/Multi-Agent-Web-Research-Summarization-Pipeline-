import axios from "axios";
import type { ResearchRequest, ResearchReportResponse } from "../types/research";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

const HISTORY_KEY = "agent_research_history";

export const apiService = {
  /**
   * Executes the research loop by making a POST to /research.
   * Archives results in local storage for history views.
   */
  async runResearch(data: ResearchRequest): Promise<ResearchReportResponse> {
    const response = await client.post<ResearchReportResponse>("/research", data);
    const report = response.data;
    
    // Add timestamp and archive report details locally
    const reportWithTimestamp = {
      ...report,
      created_at: new Date().toISOString(),
    };
    
    const history = this.getReportsFromLocal();
    history.unshift(reportWithTimestamp);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    
    return reportWithTimestamp;
  },

  /**
   * Reads the local storage history.
   */
  getReportsFromLocal(): ResearchReportResponse[] {
    const data = localStorage.getItem(HISTORY_KEY);
    return data ? JSON.parse(data) : [];
  },

  /**
   * Retrieves all completed research reports.
   */
  async getReports(): Promise<ResearchReportResponse[]> {
    return this.getReportsFromLocal();
  },

  /**
   * Retrieves a specific report by UUID.
   */
  async getReportById(id: string): Promise<ResearchReportResponse | null> {
    const list = this.getReportsFromLocal();
    return list.find((r) => r.report_id === id) || null;
  },

  /**
   * Handles downloading file formats directly from browser blobs,
   * falling back to backend static asset paths for PDF reports.
   */
  downloadReportFile(report: ResearchReportResponse, format: "markdown" | "json" | "pdf") {
    if (format === "json") {
      const dataStr = JSON.stringify(report, null, 2);
      const blob = new Blob([dataStr], { type: "application/json" });
      this._triggerDownload(blob, `report_${report.report_id}.json`);
    } else if (format === "markdown") {
      const md = this._compileMarkdown(report);
      const blob = new Blob([md], { type: "text/markdown" });
      this._triggerDownload(blob, `report_${report.report_id}.md`);
    } else if (format === "pdf") {
      // Direct user to open the report generated in the reports static directory
      const pdfUrl = `${API_BASE_URL}/reports/report_${report.report_id}.pdf`;
      window.open(pdfUrl, "_blank");
    }
  },

  _triggerDownload(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const element = document.createElement("a");
    element.href = url;
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    URL.revokeObjectURL(url);
  },

  _compileMarkdown(report: ResearchReportResponse): string {
    const sections = report.sections
      .map(
        (s) =>
          `### ${s.heading}\n\n${s.content}\n\n*Citations:* ${s.citations.join(", ")}`
      )
      .join("\n\n");

    const sources = report.sources
      .map(
        (s) =>
          `- **[${s.source_id}]** *${s.title}* — [Link](${s.url}) (Relevance: ${s.relevance_score})`
      )
      .join("\n");

    return (
      `# Research Report: ${report.topic}\n\n` +
      `**Report ID:** \`${report.report_id}\`  \n` +
      `**Wall-Clock Duration:** ${report.metadata.wall_clock_seconds}s | **Graph Cycles:** ${report.metadata.agent_interactions}\n\n` +
      `## Executive Summary\n\n${report.summary}\n\n` +
      `## Research Findings\n\n${sections}\n\n` +
      `## References\n\n${sources}\n\n` +
      `## Critique & Evaluation\n\n` +
      `- **Confidence Score:** ${report.critique.confidence_score}\n` +
      `- **Omissions / Gaps:** ${
        report.critique.gaps.length > 0 ? report.critique.gaps.join(", ") : "None"
      }\n` +
      `- **Bias Flags:** ${
        report.critique.bias_flags.length > 0
          ? report.critique.bias_flags.join(", ")
          : "None"
      }`
    );
  },
};
