import os
# Set dummy API key to satisfy SDK initialization check during tests
os.environ["GROQ_API_KEY"] = "mock-api-key-for-testing"

import pytest
from unittest.mock import AsyncMock, patch
from langgraph.graph import END
from app.graph.workflow import decide_routing, app_graph
from app.agents.planner import PlannerOutput
from app.agents.synthesizer import SynthesizedReport
from app.agents.critic import CriticOutput

def test_decide_routing():
    """
    Tests the graph's routing logic for loops and exit conditions.
    """
    # Case 1: Critic requests more research, iteration is 1 (loops back to searcher)
    state_loop = {
        "critique": {"requires_research": True},
        "iteration": 1
    }
    assert decide_routing(state_loop) == "searcher"

    # Case 2: Critic requests more research, iteration is 2 (terminates to prevent infinite loop)
    state_stop = {
        "critique": {"requires_research": True},
        "iteration": 2
    }
    assert decide_routing(state_stop) == END

    # Case 3: Critic determines report is complete, iteration is 1 (terminates)
    state_complete = {
        "critique": {"requires_research": False},
        "iteration": 1
    }
    assert decide_routing(state_complete) == END

@pytest.mark.asyncio
async def test_full_graph_workflow():
    """
    Integration test checking that a full run of the LangGraph workflow executes
    and routes nodes sequentially. Uses monkeypatched mock LLM calls.
    """
    # 1. Setup mock models
    mock_planner = PlannerOutput(
        strategy="iterative_deepening",
        queries=["quantum computing physics", "qubits scaling hardware"]
    )
    
    mock_synthesizer = SynthesizedReport(
        summary="Quantum computing summary detailing qubit technology.",
        sections=[
            {
                "heading": "Qubits and Decoherence",
                "content": "Superconducting qubits face challenges with thermal noise.",
                "citations": ["https://www.academic-research-portal.org/quantum_computing/future-of-quantum-computing.html"]
            }
        ]
    )
    
    mock_critic = CriticOutput(
        requires_research=False,
        confidence_score=0.92,
        gaps=[],
        bias_flags=[]
    )
    
    # 2. Patch the generate_structured call on GroqClient
    with patch("app.llm.groq_client.GroqClient.generate_structured") as mock_gen:
        # Mock responses in order of call: 1. Planner, 2. Synthesizer, 3. Critic
        mock_gen.side_effect = [mock_planner, mock_synthesizer, mock_critic]
        
        # 3. Define initial state
        initial_state = {
            "topic": "Future of Quantum Computing",
            "depth": "deep",
            "max_sources": 5,
            "output_format": "json",
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
        
        # 4. Invoke graph
        result = await app_graph.ainvoke(initial_state)
        
        # 5. Assert nodes populated state correctly
        assert "research_plan" in result
        assert result["research_plan"]["strategy"] == "iterative_deepening"
        assert len(result["research_plan"]["queries"]) == 2
        
        assert "search_results" in result
        assert len(result["search_results"]) > 0
        
        assert "report" in result
        assert result["report"]["summary"] == "Quantum computing summary detailing qubit technology."
        assert len(result["report"]["sections"]) == 1
        
        assert "critique" in result
        assert result["critique"]["confidence_score"] == 0.92
        assert result["critique"]["requires_research"] is False
        
        # Total interactions: Planner + Searcher + Synthesizer + Critic = 4
        assert result["meta"]["agent_interactions"] == 4
