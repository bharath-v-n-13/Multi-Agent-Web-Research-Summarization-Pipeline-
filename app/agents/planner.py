from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.llm.gemini_client import GeminiClient
from app.llm.prompts import PLANNER_SYSTEM_INSTRUCTION, PLANNER_USER_PROMPT
from app.utils.logger import logger
from app.utils.timer import async_timer

class PlannerOutput(BaseModel):
    """
    Structured schema for the Planner Agent's output.
    """
    strategy: str = Field(..., description="The chosen search strategy (e.g. breadth_first, iterative_deepening).")
    queries: List[str] = Field(..., description="List of 3-8 search queries to execute against the index.")

async def run_planner(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for the Planner Agent.
    Receives topic and depth, runs the Gemini prompt, and saves the research plan in the state.
    """
    topic = state.get("topic", "")
    depth = state.get("depth", "moderate")
    
    logger.info(f"[Planner Agent] Started research planning for topic: '{topic}' with depth: '{depth}'")
    
    client = GeminiClient()
    
    # Format the prompt
    user_prompt = PLANNER_USER_PROMPT.format(topic=topic, depth=depth)
    
    async with async_timer() as t:
        try:
            planner_response: PlannerOutput = await client.generate_structured(
                prompt=user_prompt,
                response_schema=PlannerOutput,
                system_instruction=PLANNER_SYSTEM_INSTRUCTION
            )
        except Exception as e:
            logger.error(f"[Planner Agent] API execution failed: {e}")
            raise

    logger.info(
        f"[Planner Agent] Finished. Strategy chosen: '{planner_response.strategy}'. "
        f"Generated {len(planner_response.queries)} search queries. Execution time: {t['elapsed']:.2f} seconds."
    )
    
    # Increment agent interactions count
    meta = state.get("meta", {})
    interactions = meta.get("agent_interactions", 0) + 1
    meta["agent_interactions"] = interactions
    
    # Record planner execution time
    meta["planner_duration"] = t["elapsed"]
    
    return {
        "research_plan": {
            "strategy": planner_response.strategy,
            "queries": planner_response.queries
        },
        "meta": meta
    }
