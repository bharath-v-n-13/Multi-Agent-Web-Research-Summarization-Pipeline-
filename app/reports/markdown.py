from typing import Dict, Any

def generate_markdown_report(report_data: Dict[str, Any]) -> str:
    """
    Translates the research report data structure into a formatted Markdown document.
    """
    topic = report_data.get("topic", "Research Report")
    summary = report_data.get("summary", "")
    sections = report_data.get("sections", [])
    sources = report_data.get("sources", [])
    critique = report_data.get("critique", {})
    metadata = report_data.get("metadata", {})
    report_id = report_data.get("report_id", "")

    md = []
    md.append(f"# Research Report: {topic}")
    md.append(f"**Report ID:** `{report_id}`\n")
    
    # Executive Summary
    md.append("## Executive Summary")
    md.append(summary)
    md.append("")
    
    # Sections
    md.append("## Research Details")
    for section in sections:
        md.append(f"### {section.get('heading', 'Untitled Section')}")
        md.append(section.get("content", ""))
        md.append("")
        
        # Section citations
        citations = section.get("citations", [])
        if citations:
            citations_str = ", ".join([f"<{url}>" for url in citations])
            md.append(f"*Citations:* {citations_str}\n")
            
    # Sources list
    md.append("## References and Sources")
    if sources:
        for src in sources:
            md.append(
                f"- **[{src.get('source_id')}]** *{src.get('title')}*  \n"
                f"  URL: {src.get('url')}  \n"
                f"  Relevance Score: `{src.get('relevance_score')}` | Scraped At: `{src.get('scraped_at')}`"
            )
    else:
        md.append("No reference sources found.")
    md.append("")

    # Critique section
    md.append("## Self-Critique & Quality Evaluation")
    md.append(f"- **Confidence Score:** `{critique.get('confidence_score')}`")
    
    gaps = critique.get("gaps", [])
    if gaps:
        md.append("- **Identified Knowledge Gaps:**")
        for gap in gaps:
            md.append(f"  - {gap}")
    else:
        md.append("- **Identified Knowledge Gaps:** None")
        
    bias_flags = critique.get("bias_flags", [])
    if bias_flags:
        md.append("- **Bias & Imbalance Indicators:**")
        for bias in bias_flags:
            md.append(f"  - {bias}")
    else:
        md.append("- **Bias & Imbalance Indicators:** None")
    md.append("")
    
    # Metadata metrics
    md.append("## System Metadata")
    md.append(f"- **Total URLs Searched:** {metadata.get('total_urls_visited')}")
    md.append(f"- **Agent Interactions / Graph Cycles:** {metadata.get('agent_interactions')}")
    md.append(f"- **Total Wall Clock Duration:** {metadata.get('wall_clock_seconds')} seconds")

    return "\n".join(md)
