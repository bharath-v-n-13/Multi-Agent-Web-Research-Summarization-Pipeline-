from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.agents.planner import run_planner
from app.agents.searcher import run_searcher
from app.agents.synthesizer import run_synthesizer
from app.agents.critic import run_critic
from app.utils.logger import logger

def decide_routing(state: ResearchState) -> str:
    """
    Decision node/router.
    Determines if another iteration of research is required by checking the critic's verdict
    and verifying that the iteration count is strictly below the limit of 2 loops.
    """
    critique = state.get("critique", {})
    iteration = state.get("iteration", 0)
    
    requires_research = critique.get("requires_research", False)
    
    # We allow looping back if the critic requests research AND we haven't completed 2 loops (iteration count 0 and 1).
    # Since iteration counter is incremented inside the Critic node:
    # - Run 1: Iteration goes from 0 -> 1. If requires_research=True, it loops back because 1 < 2.
    # - Run 2: Iteration goes from 1 -> 2. If requires_research=True, requires_research is forced to False by the critic, 
    #   or if not, this router will reject the loop because 2 < 2 is False.
    if requires_research and iteration < 2:
        logger.info(f"[Workflow Router] Gaps detected. Looping back to Searcher (Next iteration: {iteration})")
        return "searcher"
        
    logger.info(f"[Workflow Router] Research coverage complete or loop threshold reached (Final iteration: {iteration}). Finalizing report.")
    return END

# Initialize the workflow graph
workflow = StateGraph(ResearchState)

# Register nodes
workflow.add_node("planner", run_planner)
workflow.add_node("searcher", run_searcher)
workflow.add_node("synthesizer", run_synthesizer)
workflow.add_node("critic", run_critic)

# Establish entrypoint
workflow.set_entry_point("planner")

# Define deterministic transitions
workflow.add_edge("planner", "searcher")
workflow.add_edge("searcher", "synthesizer")
workflow.add_edge("synthesizer", "critic")

# Define conditional route from Critic
workflow.add_conditional_edges(
    "critic",
    decide_routing,
    {
        "searcher": "searcher",
        END: END
    }
)

# Compile graph
app_graph = workflow.compile()
