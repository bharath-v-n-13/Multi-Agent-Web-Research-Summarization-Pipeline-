from typing import List
from pydantic import BaseModel, Field

class ReportSection(BaseModel):
    """
    Structured component representing a section of the research report.
    """
    heading: str = Field(..., description="The heading or title of the section.")
    content: str = Field(..., description="The synthesized text content of this section.")
    citations: List[str] = Field(..., description="List of source URLs cited within this section.")

class ReportSource(BaseModel):
    """
    Detail for a source used in the synthesis of the report.
    """
    source_id: str = Field(..., description="Unique identifier for the source (e.g. S1).")
    url: str = Field(..., description="The URL of the webpage.")
    title: str = Field(..., description="The title of the page.")
    relevance_score: float = Field(..., description="The computed BM25 relevance score.")
    scraped_at: str = Field(..., description="ISO 8601 Timestamp marking when page was normalized.")

class ReportCritique(BaseModel):
    """
    The critique details assessed by the Critic Agent.
    """
    confidence_score: float = Field(..., description="Critical evaluation confidence score (0.0 to 1.0).")
    gaps: List[str] = Field(..., description="Areas or concepts identified as missing from the report.")
    bias_flags: List[str] = Field(..., description="Observed biases or skewed perspectives in the text.")

class ReportMetadata(BaseModel):
    """
    Performance and interaction statistics for the run.
    """
    total_urls_visited: int = Field(..., description="The count of crawled URLs searched during research.")
    agent_interactions: int = Field(..., description="Total count of agent interactions/turns in the graph execution.")
    wall_clock_seconds: float = Field(..., description="The wall-clock duration of the request in seconds.")

class ResearchReportResponse(BaseModel):
    """
    Complete, validated schema of the generated research report.
    """
    report_id: str = Field(..., description="UUID identifying the run.")
    topic: str = Field(..., description="The query topic.")
    summary: str = Field(..., description="Executive summary of research findings.")
    sections: List[ReportSection] = Field(..., description="List of structured research sections.")
    sources: List[ReportSource] = Field(..., description="Citations and metadata of the references used.")
    critique: ReportCritique = Field(..., description="The critique analysis details.")
    metadata: ReportMetadata = Field(..., description="Orchestration metadata metrics.")
    output_format: str = Field(..., description="The requested output format (markdown, pdf, json).")
