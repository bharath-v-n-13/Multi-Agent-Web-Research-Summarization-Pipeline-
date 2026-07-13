export interface ResearchRequest {
  topic: string;
  depth: "shallow" | "moderate" | "deep";
  max_sources: number;
  output_format: "markdown" | "pdf" | "json";
}

export interface ReportSection {
  heading: string;
  content: string;
  citations: string[];
}

export interface ReportSource {
  source_id: string;
  url: string;
  title: string;
  relevance_score: number;
  scraped_at: string;
}

export interface ReportCritique {
  confidence_score: number;
  gaps: string[];
  bias_flags: string[];
}

export interface ReportMetadata {
  total_urls_visited: number;
  agent_interactions: number;
  wall_clock_seconds: number;
}

export interface ResearchReportResponse {
  report_id: string;
  topic: string;
  summary: string;
  sections: ReportSection[];
  sources: ReportSource[];
  critique: ReportCritique;
  metadata: ReportMetadata;
  created_at?: string; // Optional field added on the frontend for history
}

export interface AgentStepProgress {
  agent: "planner" | "searcher" | "synthesizer" | "critic" | "completed";
  status: "idle" | "running" | "completed" | "failed";
  message: string;
  iteration: number;
}
