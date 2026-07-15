import uuid
import time
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.models.request import ResearchRequest
from app.models.response import ResearchReportResponse, ReportSection, ReportSource, ReportCritique, ReportMetadata
from app.utils.message_bus import get_message_bus
from app.reports.markdown import generate_markdown_report
from app.reports.json_report import generate_json_report
from app.reports.pdf import generate_pdf_report
from app.utils.logger import logger
from app.utils.timer import async_timer

router = APIRouter()

# Create reports output directory
reports_dir = Path("reports")
reports_dir.mkdir(exist_ok=True)

@router.post("/research", response_model=ResearchReportResponse)
async def perform_research(request: ResearchRequest) -> ResearchReportResponse:
    """
    Triggers the autonomous research graph workflow.
    Validates input schemas, coordinates agent node executions, logs telemetry, 
    and exports the result to the requested format (Markdown, JSON, or PDF).
    """
    logger.info(f"[API] Received research request. Topic: '{request.topic}' | Depth: '{request.depth}'")
    
    # Initialize shared state
    state = {
        "topic": request.topic,
        "depth": request.depth,
        "max_sources": request.max_sources,
        "output_format": request.output_format,
        "research_plan": {},
        "search_results": [],
        "scraped_documents": [],
        "report": {},
        "critique": {},
        "iteration": 0,
        "meta": {
            "agent_interactions": 0,
            "total_urls_visited": 0,
            "wall_clock_seconds": 0.0
        }
    }
    
    # Generate unique ID for this report run
    report_id = str(uuid.uuid4())
    
    bus = get_message_bus()
    
    # Publish request parameters to message bus
    request_payload = {
        "report_id": report_id,
        "topic": request.topic,
        "depth": request.depth,
        "max_sources": request.max_sources,
        "output_format": request.output_format
    }
    
    async with async_timer() as wall_clock:
        try:
            await bus.publish("stream:research_requests", request_payload)
            
            # Poll for state completion (or timeout)
            from app.agents.supervisor import SupervisorAgent
            supervisor = SupervisorAgent(bus=bus)
            
            final_state = None
            max_wait = 300.0  # 5 minutes global timeout
            poll_interval = 1.0
            elapsed = 0.0
            
            while elapsed < max_wait:
                state_data = await supervisor.get_state(report_id)
                if state_data:
                    status = state_data.get("status")
                    if status in ["completed", "failed", "timeout"]:
                        final_state = state_data
                        break
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval
                
            if not final_state:
                raise HTTPException(
                    status_code=504,
                    detail="The research request timed out at the API gateway."
                )
                
            if final_state.get("status") in ["failed", "timeout"]:
                raise HTTPException(
                    status_code=500,
                    detail=final_state.get("error", "An error occurred during agent execution.")
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[API] Error running research workflow: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred during agent execution: {str(e)}"
            )
            
    elapsed_seconds = round(wall_clock["elapsed"], 2)
    logger.info(f"[API] Research workflow completed in {elapsed_seconds} seconds.")
    
    # Extract results from final state
    report = final_state.get("report", {})
    search_results = final_state.get("search_results", [])
    scraped_docs = final_state.get("scraped_documents", [])
    critique = final_state.get("critique", {})
    meta = final_state.get("meta", {})
    
    if not report:
        raise HTTPException(
            status_code=500,
            detail="The research system failed to generate a report."
        )
        
    # Map raw scraped timestamps to search results
    scrape_timestamp_map = {doc["url"]: doc["timestamp"] for doc in scraped_docs}
    
    # Build sections for response model
    validated_sections = [
        ReportSection(
            heading=s.get("heading", "Untitled Section"),
            content=s.get("content", ""),
            citations=s.get("citations", [])
        ) for s in report.get("sections", [])
    ]
    
    # Build sources for response model
    validated_sources = [
        ReportSource(
            source_id=s.get("source_id", ""),
            url=s.get("url", ""),
            title=s.get("title", ""),
            relevance_score=s.get("score", 0.0),
            scraped_at=scrape_timestamp_map.get(s.get("url"), "")
        ) for s in search_results
    ]
    
    # Build critique details
    validated_critique = ReportCritique(
        confidence_score=critique.get("confidence_score", 0.0),
        gaps=critique.get("gaps", []),
        bias_flags=critique.get("bias_flags", [])
    )
    
    # Compile execution telemetry metadata
    validated_metadata = ReportMetadata(
        total_urls_visited=len(search_results),
        agent_interactions=meta.get("agent_interactions", 0),
        wall_clock_seconds=elapsed_seconds
    )
    
    # Assemble final response model
    response_payload = ResearchReportResponse(
        report_id=report_id,
        topic=request.topic,
        summary=report.get("summary", ""),
        sections=validated_sections,
        sources=validated_sources,
        critique=validated_critique,
        metadata=validated_metadata,
        output_format=request.output_format
    )
    
    # Export report file based on format selection
    report_dict = response_payload.model_dump()
    try:
        if request.output_format == "markdown":
            md_content = generate_markdown_report(report_dict)
            file_path = reports_dir / f"report_{report_id}.md"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            logger.info(f"[API] Exported markdown report to: {file_path}")
            
        elif request.output_format == "json":
            json_content = generate_json_report(report_dict)
            file_path = reports_dir / f"report_{report_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)
            logger.info(f"[API] Exported JSON report to: {file_path}")
            
        elif request.output_format == "pdf":
            pdf_bytes = generate_pdf_report(report_dict)
            file_path = reports_dir / f"report_{report_id}.pdf"
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)
            logger.info(f"[API] Exported PDF report to: {file_path}")
            
    except Exception as export_error:
        # Log error but don't fail request if writing file fails
        logger.error(f"[API] Failed to write exported report to disk: {export_error}")
        
    return response_payload
