from typing import Dict, Any
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(report_data: Dict[str, Any]) -> bytes:
    """
    Generates a beautifully formatted PDF document binary from report data using ReportLab.
    Ensures safe font rendering, dynamic text wrapping in tables, and correct margins.
    """
    buffer = io.BytesIO()
    
    # Margins are 0.75 inches (54 points)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Core color palette
    # Primary: Sleek dark navy, secondary: steel teal accent, text: off-black
    primary_color = colors.HexColor('#002B49')
    secondary_color = colors.HexColor('#008080')
    text_color = colors.HexColor('#2D3748')
    muted_text_color = colors.HexColor('#718096')
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=8
    )
    
    h1_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=15,
        leading=19,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SubSectionHeader',
        parent=styles['Heading3'],
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBodyText',
        parent=styles['BodyText'],
        fontSize=9.5,
        leading=13.5,
        textColor=text_color,
        spaceAfter=8
    )

    citation_style = ParagraphStyle(
        'CitationText',
        parent=styles['Italic'],
        fontSize=7.5,
        leading=10.5,
        textColor=muted_text_color,
        spaceAfter=10
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11.5,
        textColor=muted_text_color
    )

    story = []
    
    topic = report_data.get("topic", "Research Report")
    summary = report_data.get("summary", "")
    sections = report_data.get("sections", [])
    sources = report_data.get("sources", [])
    critique = report_data.get("critique", {})
    metadata = report_data.get("metadata", {})
    report_id = report_data.get("report_id", "")
    
    # 1. Report Title block
    story.append(Paragraph(f"Research Report: {topic}", title_style))
    story.append(Paragraph(f"Report ID: {report_id}", meta_style))
    story.append(Spacer(1, 12))
    
    # 2. Executive Summary Section
    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 8))
    
    # 3. Detailed Findings Sections
    story.append(Paragraph("Research Findings", h1_style))
    for section in sections:
        heading = section.get('heading', 'Untitled Section')
        content = section.get('content', '')
        story.append(Paragraph(heading, h2_style))
        story.append(Paragraph(content, body_style))
        
        # Append cited sources if present in this section
        citations = section.get("citations", [])
        if citations:
            cites_formatted = "<b>Citations:</b> " + ", ".join([f"&lt;{url}&gt;" for url in citations])
            story.append(Paragraph(cites_formatted, citation_style))
            
    story.append(Spacer(1, 10))
    
    # 4. Sources Appendix (On a new page)
    story.append(PageBreak())
    story.append(Paragraph("References and Sources", h1_style))
    
    if sources:
        # Table layout to present sources cleanly
        table_data = [[
            Paragraph("<b>ID</b>", meta_style),
            Paragraph("<b>Reference details</b>", meta_style),
            Paragraph("<b>BM25 Score</b>", meta_style)
        ]]
        
        for src in sources:
            source_id = src.get("source_id", "")
            title_text = src.get("title", "")
            url_text = src.get("url", "")
            score = f"{src.get('relevance_score', 0.0):.4f}"
            scraped = src.get("scraped_at", "")
            
            # Format row HTML blocks to wrap correctly
            details = f"<b>{title_text}</b><br/><font color='#718096'>{url_text}</font><br/><font size='7' color='#A0AEC0'>Scraped: {scraped}</font>"
            
            table_data.append([
                Paragraph(source_id, meta_style),
                Paragraph(details, meta_style),
                Paragraph(score, meta_style)
            ])
            
        # 504 total printable width (Letter = 612 - left/right margins 108)
        # Column split: ID = 35pt, Source info = 419pt, Relevance Score = 50pt
        src_table = Table(table_data, colWidths=[35, 419, 50])
        src_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FAFC')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(src_table)
    else:
        story.append(Paragraph("No sources found for this report.", body_style))
        
    story.append(Spacer(1, 12))
    
    # 5. Critique Details
    story.append(Paragraph("Self-Critique & Quality Evaluation", h1_style))
    story.append(Paragraph(f"<b>Confidence Score:</b> {critique.get('confidence_score', 0.0):.2f}", body_style))
    
    gaps_list = critique.get("gaps", [])
    if gaps_list:
        gaps_text = "<b>Knowledge Gaps Identified:</b><br/>" + "<br/>".join([f"• {gap}" for gap in gaps_list])
        story.append(Paragraph(gaps_text, body_style))
    else:
        story.append(Paragraph("<b>Knowledge Gaps Identified:</b> None", body_style))
        
    bias_list = critique.get("bias_flags", [])
    if bias_list:
        bias_text = "<b>Bias & Balance Flags:</b><br/>" + "<br/>".join([f"• {bias}" for bias in bias_list])
        story.append(Paragraph(bias_text, body_style))
    else:
        story.append(Paragraph("<b>Bias & Balance Flags:</b> None", body_style))
        
    story.append(Spacer(1, 10))
    
    # 6. Run Telemetry
    story.append(Paragraph("System Telemetry", h1_style))
    telemetry = (
        f"• <b>Total URL Sources Searched:</b> {metadata.get('total_urls_visited', 0)}<br/>"
        f"• <b>Agent Graph Interactions:</b> {metadata.get('agent_interactions', 0)} cycles<br/>"
        f"• <b>Execution Duration:</b> {metadata.get('wall_clock_seconds', 0.0):.2f} seconds<br/>"
    )
    story.append(Paragraph(telemetry, body_style))
    
    # Build Document
    doc.build(story)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
