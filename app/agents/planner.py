from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.llm.groq_client import GroqClient
from app.llm.prompts import PLANNER_SYSTEM_INSTRUCTION, PLANNER_USER_PROMPT
from app.utils.logger import logger
from app.utils.timer import async_timer
from app.agents.base import BaseWorkerAgent
from app.utils.message_bus import MessageBus

class PlannerOutput(BaseModel):
    """
    Structured schema for the Planner Agent's output.
    """
    strategy: str = Field(..., description="The chosen search strategy (e.g. breadth_first, iterative_deepening).")
    queries: List[str] = Field(..., description="List of 3-8 search queries to execute against the index.")


class PlannerAgent(BaseWorkerAgent):
    """
    Planner Agent Worker process.
    Receives research requests, generates a list of sub-queries, and posts results.
    """
    def __init__(self, concurrency_limit: int = 10, bus: Optional[MessageBus] = None):
        super().__init__(
            agent_name="PlannerAgent",
            input_stream="stream:planner",
            output_stream="stream:planner:completed",
            concurrency_limit=concurrency_limit,
            bus=bus
        )

    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = message_data.get("topic", "")
        depth = message_data.get("depth", "moderate")
        
        logger.info(f"[Planner Worker] Started research planning for topic: '{topic}' with depth: '{depth}'")
        
        client = GroqClient()
        user_prompt = PLANNER_USER_PROMPT.format(topic=topic, depth=depth)
        
        async with async_timer() as t:
            try:
                # Add basic retry logic for rate limits
                attempts = 3
                for attempt in range(attempts):
                    try:
                        planner_response: PlannerOutput = await client.generate_structured(
                            prompt=user_prompt,
                            response_schema=PlannerOutput,
                            system_instruction=PLANNER_SYSTEM_INSTRUCTION
                        )
                        break
                    except Exception as e:
                        if attempt == attempts - 1:
                            raise
                        logger.warning(f"[Planner Worker] Rate limit or transient error encountered: {e}. Retrying...")
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"[Planner Worker] API execution failed: {e}")
                raise

        logger.info(
            f"[Planner Worker] Finished. Strategy chosen: '{planner_response.strategy}'. "
            f"Generated {len(planner_response.queries)} search queries. Execution time: {t['elapsed']:.2f} seconds."
        )
        
        # Track metadata updates
        meta = message_data.get("meta", {})
        interactions = meta.get("agent_interactions", 0) + 1
        meta["agent_interactions"] = interactions
        meta["planner_duration"] = t["elapsed"]
        
        return {
            "research_plan": {
                "strategy": planner_response.strategy,
                "queries": planner_response.queries
            },
            "meta": meta
        }


# Keep compatibility for existing imports or LangGraph test cases
async def run_planner(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback LangGraph node for the Planner Agent.
    """
    agent = PlannerAgent()
    return await agent.process_message(state)
