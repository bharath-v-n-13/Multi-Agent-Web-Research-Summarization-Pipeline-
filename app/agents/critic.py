import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.llm.gemini_client import GeminiClient
from app.llm.prompts import CRITIC_SYSTEM_INSTRUCTION, CRITIC_USER_PROMPT
from app.utils.logger import logger
from app.utils.timer import async_timer

class CriticOutput(BaseModel):
    """
    Pydantic schema for the Critic Agent's output.
    """
    requires_research: bool = Field(..., description="True if additional search is required to cover gaps.")
    confidence_score: float = Field(..., description="Overall confidence score (0.0 to 1.0) assessing report coverage.")
    gaps: List[str] = Field(..., description="Topics or queries to search to address the gaps.")
    bias_flags: List[str] = Field(..., description="Identified instances of bias or imbalance in the report.")

async def run_critic(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for the Critic Agent.
    Evaluates the current report against the research topic, determines if more research is needed,
    increments the iteration counter, and saves critique data in the state.
    """
    topic = state.get("topic", "")
    report = state.get("report", {})
    iteration = state.get("iteration", 0)
    
    logger.info(f"[Critic Agent] Starting critique evaluation for topic: '{topic}' (Iteration: {iteration})")
    
    if not report:
        logger.warning("[Critic Agent] No report found to critique. Forcing research completion.")
        return {
            "critique": {
                "confidence_score": 0.0,
                "gaps": ["No report generated"],
                "bias_flags": ["No report generated"],
                "requires_research": False
            },
            "iteration": iteration + 1
        }
        
    client = GeminiClient()
    
    # Format the user prompt
    user_prompt = CRITIC_USER_PROMPT.format(
        topic=topic,
        report=json.dumps(report, indent=2)
    )
    
    async with async_timer() as t:
        try:
            critic_response: CriticOutput = await client.generate_structured(
                prompt=user_prompt,
                response_schema=CriticOutput,
                system_instruction=CRITIC_SYSTEM_INSTRUCTION
            )
        except Exception as e:
            logger.error(f"[Critic Agent] Critique evaluation failed: {e}")
            raise
            
    # Force requires_research to False if we have reached the maximum iteration limit (2 loops)
    # The maximum loops is 2, so if the iteration is already 1, after this run we increment to 2 and stop.
    requires_research = critic_response.requires_research
    if iteration >= 1:
        logger.info(f"[Critic Agent] Maximum loop limit reached (iteration={iteration}). Forcing requires_research=False.")
        requires_research = False

    logger.info(
        f"[Critic Agent] Finished. Confidence score: {critic_response.confidence_score:.2f}. "
        f"Requires more research: {requires_research}. Identified {len(critic_response.gaps)} gaps. "
        f"Execution time: {t['elapsed']:.2f} seconds."
    )
    
    # Increment iteration count
    next_iteration = iteration + 1
    
    # Increment agent interactions count
    meta = state.get("meta", {})
    interactions = meta.get("agent_interactions", 0) + 1
    meta["agent_interactions"] = interactions
    
    # Record critic execution duration
    meta["critic_duration"] = t["elapsed"]
    
    return {
        "critique": {
            "confidence_score": critic_response.confidence_score,
            "gaps": critic_response.gaps,
            "bias_flags": critic_response.bias_flags,
            "requires_research": requires_research
        },
        "iteration": next_iteration,
        "meta": meta
    }
