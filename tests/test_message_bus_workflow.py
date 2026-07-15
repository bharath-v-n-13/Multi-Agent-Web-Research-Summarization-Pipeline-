import os
# Ensure dummy API key is set
os.environ["GROQ_API_KEY"] = "mock-api-key-for-testing"
os.environ["USE_REDIS"] = "false"

import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.utils.message_bus import InMemoryMessageBus
from app.agents.planner import PlannerAgent, PlannerOutput
from app.agents.searcher import SearcherAgent
from app.agents.synthesizer import SynthesizerAgent, SynthesizedReport
from app.agents.critic import CriticAgent, CriticOutput
from app.agents.supervisor import SupervisorAgent

@pytest.mark.asyncio
async def test_message_bus_integration_workflow():
    # 1. Setup in-memory bus
    bus = InMemoryMessageBus()
    
    # 2. Patch Groq Client structured response outputs
    mock_planner = PlannerOutput(
        strategy="breadth_first",
        queries=["quantum computing speedup", "qubit technology progress"]
    )
    
    mock_synthesizer = SynthesizedReport(
        summary="An in-depth summary of quantum hardware engineering advances.",
        sections=[
            {
                "heading": "Quantum Scaling Limits",
                "content": "Superconducting qubits require sub-Kelvin refrigeration to avoid thermal noise.",
                "citations": ["https://www.academic-research-portal.org/quantum_computing/future-of-quantum-computing.html"]
            }
        ]
    )
    
    mock_critic = CriticOutput(
        requires_research=False,
        confidence_score=0.95,
        gaps=[],
        bias_flags=[]
    )
    
    with patch("app.llm.groq_client.GroqClient.generate_structured") as mock_gen:
        # Define mock response order: Planner -> Synthesizer -> Critic
        mock_gen.side_effect = [mock_planner, mock_synthesizer, mock_critic]
        
        # 3. Instantiate Workers with in-memory bus
        planner = PlannerAgent(bus=bus)
        searcher = SearcherAgent(bus=bus)
        synthesizer = SynthesizerAgent(bus=bus)
        critic = CriticAgent(bus=bus)
        supervisor = SupervisorAgent(bus=bus)
        
        # 4. Start all agent worker loops as background tasks
        tasks = [
            asyncio.create_task(planner.run_forever()),
            asyncio.create_task(searcher.run_forever()),
            asyncio.create_task(synthesizer.run_forever()),
            asyncio.create_task(critic.run_forever()),
            asyncio.create_task(supervisor.run_forever())
        ]
        
        # Allow workers to initialize
        await asyncio.sleep(0.5)
        
        # 5. Publish start message to stream:research_requests
        report_id = "test-bus-report-id"
        request_payload = {
            "report_id": report_id,
            "topic": "Future of Quantum Computing",
            "depth": "shallow",
            "max_sources": 5,
            "output_format": "json"
        }
        await bus.publish("stream:research_requests", request_payload)
        
        # 6. Poll for completion status
        final_state = None
        for _ in range(50):
            state = await supervisor.get_state(report_id)
            if state and state.get("status") in ["completed", "failed", "timeout"]:
                final_state = state
                break
            await asyncio.sleep(0.2)
            
        # 7. Shutdown workers
        planner.stop()
        searcher.stop()
        synthesizer.stop()
        critic.stop()
        supervisor.stop()
        
        for t in tasks:
            t.cancel()
            
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 8. Assertions
        assert final_state is not None, "Pipeline did not complete in time"
        assert final_state["status"] == "completed"
        assert final_state["research_plan"]["strategy"] == "breadth_first"
        assert len(final_state["search_results"]) > 0
        assert final_state["report"]["summary"] == "An in-depth summary of quantum hardware engineering advances."
        assert len(final_state["report"]["sections"]) == 1
        assert final_state["critique"]["confidence_score"] == 0.95
        assert final_state["meta"]["agent_interactions"] == 4
        assert final_state["meta"]["wall_clock_seconds"] > 0
