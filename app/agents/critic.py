import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.llm.groq_client import GroqClient
from app.llm.prompts import CRITIC_SYSTEM_INSTRUCTION, CRITIC_USER_PROMPT
from app.utils.logger import logger
from app.utils.timer import async_timer
from app.agents.base import BaseWorkerAgent
from app.utils.message_bus import MessageBus

class CriticOutput(BaseModel):
    """
    Pydantic schema for the Critic Agent's output.
    """
    requires_research: bool = Field(..., description="True if additional search is required to cover gaps.")
    confidence_score: float = Field(..., description="Overall confidence score (0.0 to 1.0) assessing report coverage.")
    gaps: List[str] = Field(..., description="Topics or queries to search to address the gaps.")
    bias_flags: List[str] = Field(..., description="Identified instances of bias or imbalance in the report.")


class CriticAgent(BaseWorkerAgent):
    """
    Critic Agent Worker process.
    Evaluates the current synthesized report against the topic and identifies gaps/biases.
    """
    def __init__(self, concurrency_limit: int = 10, bus: Optional[MessageBus] = None):
        super().__init__(
            agent_name="CriticAgent",
            input_stream="stream:critic",
            output_stream="stream:critic:completed",
            concurrency_limit=concurrency_limit,
            bus=bus
        )

    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        topic = message_data.get("topic", "")
        report = message_data.get("report", {})
        iteration = message_data.get("iteration", 0)
        
        logger.info(f"[Critic Worker] Starting critique evaluation for topic: '{topic}' (Iteration: {iteration})")
        
        if not report:
            logger.warning("[Critic Worker] No report found to critique. Forcing research completion.")
            return {
                "critique": {
                    "confidence_score": 0.0,
                    "gaps": ["No report generated"],
                    "bias_flags": ["No report generated"],
                    "requires_research": False
                },
                "iteration": iteration + 1
            }
            
        client = GroqClient()
        user_prompt = CRITIC_USER_PROMPT.format(
            topic=topic,
            report=json.dumps(report, indent=2)
        )
        
        async with async_timer() as t:
            try:
                # Add basic retry logic for rate limits
                attempts = 3
                for attempt in range(attempts):
                    try:
                        critic_response: CriticOutput = await client.generate_structured(
                            prompt=user_prompt,
                            response_schema=CriticOutput,
                            system_instruction=CRITIC_SYSTEM_INSTRUCTION
                        )
                        break
                    except Exception as e:
                        if attempt == attempts - 1:
                            raise
                        logger.warning(f"[Critic Worker] Rate limit or transient error: {e}. Retrying...")
                        import asyncio
                        await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"[Critic Worker] Critique evaluation failed: {e}")
                raise
                
        requires_research = critic_response.requires_research
        # Force requires_research to False if we have reached the maximum iteration limit (2 loops)
        if iteration >= 1:
            logger.info(f"[Critic Worker] Maximum loop limit reached (iteration={iteration}). Forcing requires_research=False.")
            requires_research = False

        logger.info(
            f"[Critic Worker] Finished. Confidence score: {critic_response.confidence_score:.2f}. "
            f"Requires more research: {requires_research}. Identified {len(critic_response.gaps)} gaps. "
            f"Execution time: {t['elapsed']:.2f} seconds."
        )
        
        next_iteration = iteration + 1
        
        meta = message_data.get("meta", {})
        interactions = meta.get("agent_interactions", 0) + 1
        meta["agent_interactions"] = interactions
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


# Keep compatibility for existing imports
async def run_critic(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback LangGraph node for the Critic Agent.
    """
    agent = CriticAgent()
    return await agent.process_message(state)
