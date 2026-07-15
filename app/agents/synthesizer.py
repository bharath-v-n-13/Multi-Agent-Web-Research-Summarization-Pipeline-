from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.llm.groq_client import GroqClient
from app.llm.prompts import SYNTHESIZER_SYSTEM_INSTRUCTION, SYNTHESIZER_USER_PROMPT
from app.utils.logger import logger
from app.utils.timer import async_timer
from app.agents.base import BaseWorkerAgent
from app.utils.message_bus import MessageBus

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


class SynthesizerAgent(BaseWorkerAgent):
    """
    Synthesizer Agent Worker process.
    Aggregates the scraped documents and research plan, and compiles a structured report.
    """
    def __init__(self, concurrency_limit: int = 10, bus: Optional[MessageBus] = None):
        super().__init__(
            agent_name="SynthesizerAgent",
            input_stream="stream:synthesizer",
            output_stream="stream:synthesizer:completed",
            concurrency_limit=concurrency_limit,
            bus=bus
        )

    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = message_data.get("topic", "")
        plan = message_data.get("research_plan", {})
        scraped_docs = message_data.get("scraped_documents", [])
        
        logger.info(f"[Synthesizer Worker] Starting synthesis of report for topic: '{topic}'")
        
        if not scraped_docs:
            logger.warning("[Synthesizer Worker] No documents available for synthesis. Creating empty report stub.")
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
        
        user_prompt = SYNTHESIZER_USER_PROMPT.format(
            topic=topic,
            plan=plan,
            documents=documents_str
        )
        
        client = GroqClient()
        
        async with async_timer() as t:
            try:
                # Add basic retry logic for rate limits
                attempts = 3
                for attempt in range(attempts):
                    try:
                        report_response: SynthesizedReport = await client.generate_structured(
                            prompt=user_prompt,
                            response_schema=SynthesizedReport,
                            system_instruction=SYNTHESIZER_SYSTEM_INSTRUCTION
                        )
                        break
                    except Exception as e:
                        if attempt == attempts - 1:
                            raise
                        logger.warning(f"[Synthesizer Worker] Rate limit or transient error: {e}. Retrying...")
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"[Synthesizer Worker] Report synthesis failed: {e}")
                raise

        logger.info(
            f"[Synthesizer Worker] Finished. Compiled {len(report_response.sections)} report sections. "
            f"Execution time: {t['elapsed']:.2f} seconds."
        )
        
        meta = message_data.get("meta", {})
        interactions = meta.get("agent_interactions", 0) + 1
        meta["agent_interactions"] = interactions
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


# Keep compatibility for existing imports
async def run_synthesizer(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback LangGraph node for the Synthesizer Agent.
    """
    agent = SynthesizerAgent()
    return await agent.process_message(state)
