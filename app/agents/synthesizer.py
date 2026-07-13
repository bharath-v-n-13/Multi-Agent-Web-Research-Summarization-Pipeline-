from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.llm.groq_client import GroqClient
from app.llm.prompts import SYNTHESIZER_SYSTEM_INSTRUCTION, SYNTHESIZER_USER_PROMPT
from app.utils.logger import logger
from app.utils.timer import async_timer

class SynthesizedSection(BaseModel):
    """
    Sub-schema for sections output by Groq.
    """
    heading: str = Field(..., description="The heading of this section.")
    content: str = Field(..., description="The comprehensive research content for this section.")
    citations: List[str] = Field(..., description="List of source URLs cited within this section content.")

class SynthesizedReport(BaseModel):
    """
    Main schema for the Synthesizer Agent's output.
    """
    summary: str = Field(..., description="The executive summary of research findings.")
    sections: List[SynthesizedSection] = Field(..., description="Detailed sections covering various aspects of the topic.")

async def run_synthesizer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for the Synthesizer Agent.
    Aggregates the scraped documents and research plan, prompts Groq to synthesize
    a structured report, and saves it in the state.
    """
    topic = state.get("topic", "")
    plan = state.get("research_plan", {})
    scraped_docs = state.get("scraped_documents", [])
    
    logger.info(f"[Synthesizer Agent] Starting synthesis of report for topic: '{topic}'")
    
    if not scraped_docs:
        logger.warning("[Synthesizer Agent] No documents available for synthesis. Creating empty report stub.")
        stub_report = {
            "summary": f"No information could be found or crawled for the topic: {topic}.",
            "sections": [
                {
                    "heading": "Introduction",
                    "content": "No relevant documents were retrieved by the search system, hence a detailed report could not be compiled.",
                    "citations": []
                }
            ]
        }
        return {"report": stub_report}

    # Format the documents list for the prompt
    formatted_docs = []
    for doc in scraped_docs:
        formatted_docs.append(
            f"Source ID: {doc['source_id']}\n"
            f"URL: {doc['url']}\n"
            f"Title: {doc['title']}\n"
            f"Content:\n{doc['content']}\n"
            f"----------------------------------------"
        )
    documents_str = "\n".join(formatted_docs)
    
    # Format the user prompt
    user_prompt = SYNTHESIZER_USER_PROMPT.format(
        topic=topic,
        plan=plan,
        documents=documents_str
    )
    
    client = GroqClient()
    
    async with async_timer() as t:
        try:
            report_response: SynthesizedReport = await client.generate_structured(
                prompt=user_prompt,
                response_schema=SynthesizedReport,
                system_instruction=SYNTHESIZER_SYSTEM_INSTRUCTION
            )
        except Exception as e:
            logger.error(f"[Synthesizer Agent] Report synthesis failed: {e}")
            raise

    logger.info(
        f"[Synthesizer Agent] Finished. Compiled {len(report_response.sections)} report sections. "
        f"Execution time: {t['elapsed']:.2f} seconds."
    )
    
    # Increment agent interactions count
    meta = state.get("meta", {})
    interactions = meta.get("agent_interactions", 0) + 1
    meta["agent_interactions"] = interactions
    
    # Record synthesizer execution duration
    meta["synthesizer_duration"] = t["elapsed"]
    
    return {
        "report": {
            "summary": report_response.summary,
            "sections": [
                {
                    "heading": s.heading,
                    "content": s.content,
                    "citations": s.citations
                } for s in report_response.sections
            ]
        },
        "meta": meta
    }
