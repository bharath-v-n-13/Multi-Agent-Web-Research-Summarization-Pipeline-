import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from app.utils.message_bus import MessageBus, get_message_bus, RedisMessageBus
from app.utils.logger import logger

class SupervisorAgent:
    """
    Supervisor Agent that coordinates state transitions, tracks agent states,
    handles errors and retries, and enforces a global 5-minute timeout.
    """
    def __init__(self, bus: Optional[MessageBus] = None):
        self.bus = bus or get_message_bus()
        self.states: Dict[str, Dict[str, Any]] = {}  # In-memory fallback
        self.running = False
        self.active_tasks = []
        self.retry_limit = 2  # Max retries per stage

    async def get_state(self, report_id: str) -> Dict[str, Any]:
        if isinstance(self.bus, RedisMessageBus):
            val = await self.bus.client.get(f"research:state:{report_id}")
            return json.loads(val) if val else {}
        return self.states.get(report_id, {})

    async def save_state(self, report_id: str, state: Dict[str, Any]):
        if isinstance(self.bus, RedisMessageBus):
            # Store in Redis with 24 hour expiration
            await self.bus.client.set(f"research:state:{report_id}", json.dumps(state), ex=86400)
        else:
            self.states[report_id] = state

    async def run_forever(self):
        self.running = True
        logger.info("[Supervisor] Starting supervisor service. Enforcing 5-minute global timeouts...")
        
        # Start all listener tasks concurrently
        self.active_tasks = [
            asyncio.create_task(self.listen_requests()),
            asyncio.create_task(self.listen_planner()),
            asyncio.create_task(self.listen_searcher()),
            asyncio.create_task(self.listen_synthesizer()),
            asyncio.create_task(self.listen_critic()),
            asyncio.create_task(self.listen_errors()),
            asyncio.create_task(self.timeout_watcher())
        ]
        
        try:
            await asyncio.gather(*self.active_tasks)
        except asyncio.CancelledError:
            logger.info("[Supervisor] Supervisor loop cancelled.")
        finally:
            self.running = False

    def stop(self):
        self.running = False
        for t in self.active_tasks:
            t.cancel()

    async def listen_requests(self):
        group_name = "group-supervisor-requests"
        consumer_name = "consumer-supervisor"
        while self.running:
            try:
                messages = await self.bus.read_stream(
                    stream="stream:research_requests",
                    group=group_name,
                    consumer=consumer_name,
                    count=5,
                    block_ms=1000
                )
                for msg_id, data in messages:
                    report_id = data.get("report_id")
                    if not report_id:
                        logger.warning(f"[Supervisor] Received request without report_id: {data}")
                        await self.bus.acknowledge("stream:research_requests", group_name, msg_id)
                        continue
                    
                    logger.info(f"[Supervisor] New research request received: {report_id} for topic '{data.get('topic')}'")
                    
                    # Create initial state
                    state = {
                        "topic": data["topic"],
                        "depth": data.get("depth", "moderate"),
                        "max_sources": int(data.get("max_sources", 20)),
                        "output_format": data.get("output_format", "json"),
                        "iteration": 0,
                        "current_stage": "planner",
                        "start_time": time.time(),
                        "retries": {
                            "planner": 0,
                            "searcher": 0,
                            "synthesizer": 0,
                            "critic": 0
                        },
                        "meta": {
                            "agent_interactions": 0,
                            "total_urls_visited": 0,
                            "wall_clock_seconds": 0.0
                        }
                    }
                    await self.save_state(report_id, state)
                    
                    # Transition to Planner
                    planner_input = {
                        "report_id": report_id,
                        "topic": state["topic"],
                        "depth": state["depth"],
                        "meta": state["meta"]
                    }
                    await self.bus.publish("stream:planner", planner_input)
                    await self.bus.acknowledge("stream:research_requests", group_name, msg_id)
                    
            except Exception as e:
                logger.error(f"[Supervisor] Error in request listener: {e}")
                await asyncio.sleep(1.0)

    async def listen_planner(self):
        group_name = "group-supervisor-planner"
        consumer_name = "consumer-supervisor"
        while self.running:
            try:
                messages = await self.bus.read_stream(
                    stream="stream:planner:completed",
                    group=group_name,
                    consumer=consumer_name,
                    count=5,
                    block_ms=1000
                )
                for msg_id, data in messages:
                    report_id = data.get("report_id")
                    state = await self.get_state(report_id)
                    if not state:
                        await self.bus.acknowledge("stream:planner:completed", group_name, msg_id)
                        continue
                    
                    logger.info(f"[Supervisor] [{report_id}] Planner agent finished.")
                    
                    # Update state
                    state["research_plan"] = data.get("research_plan", {})
                    state["meta"] = data.get("meta", state["meta"])
                    state["current_stage"] = "searcher"
                    await self.save_state(report_id, state)
                    
                    # Trigger Searcher
                    searcher_input = {
                        "report_id": report_id,
                        "topic": state["topic"],
                        "max_sources": state["max_sources"],
                        "iteration": state["iteration"],
                        "research_plan": state["research_plan"],
                        "meta": state["meta"]
                    }
                    await self.bus.publish("stream:searcher", searcher_input)
                    await self.bus.acknowledge("stream:planner:completed", group_name, msg_id)
                    
            except Exception as e:
                logger.error(f"[Supervisor] Error in planner response listener: {e}")
                await asyncio.sleep(1.0)

    async def listen_searcher(self):
        group_name = "group-supervisor-searcher"
        consumer_name = "consumer-supervisor"
        while self.running:
            try:
                messages = await self.bus.read_stream(
                    stream="stream:searcher:completed",
                    group=group_name,
                    consumer=consumer_name,
                    count=5,
                    block_ms=1000
                )
                for msg_id, data in messages:
                    report_id = data.get("report_id")
                    state = await self.get_state(report_id)
                    if not state:
                        await self.bus.acknowledge("stream:searcher:completed", group_name, msg_id)
                        continue
                    
                    logger.info(f"[Supervisor] [{report_id}] Searcher agent finished.")
                    
                    # Update state
                    state["search_results"] = data.get("search_results", [])
                    state["scraped_documents"] = data.get("scraped_documents", [])
                    state["meta"] = data.get("meta", state["meta"])
                    state["current_stage"] = "synthesizer"
                    await self.save_state(report_id, state)
                    
                    # Trigger Synthesizer
                    synth_input = {
                        "report_id": report_id,
                        "topic": state["topic"],
                        "research_plan": state.get("research_plan", {}),
                        "scraped_documents": state["scraped_documents"],
                        "meta": state["meta"]
                    }
                    await self.bus.publish("stream:synthesizer", synth_input)
                    await self.bus.acknowledge("stream:searcher:completed", group_name, msg_id)
                    
            except Exception as e:
                logger.error(f"[Supervisor] Error in searcher response listener: {e}")
                await asyncio.sleep(1.0)

    async def listen_synthesizer(self):
        group_name = "group-supervisor-synthesizer"
        consumer_name = "consumer-supervisor"
        while self.running:
            try:
                messages = await self.bus.read_stream(
                    stream="stream:synthesizer:completed",
                    group=group_name,
                    consumer=consumer_name,
                    count=5,
                    block_ms=1000
                )
                for msg_id, data in messages:
                    report_id = data.get("report_id")
                    state = await self.get_state(report_id)
                    if not state:
                        await self.bus.acknowledge("stream:synthesizer:completed", group_name, msg_id)
                        continue
                    
                    logger.info(f"[Supervisor] [{report_id}] Synthesizer agent finished.")
                    
                    # Update state
                    state["report"] = data.get("report", {})
                    state["meta"] = data.get("meta", state["meta"])
                    state["current_stage"] = "critic"
                    await self.save_state(report_id, state)
                    
                    # Trigger Critic
                    critic_input = {
                        "report_id": report_id,
                        "topic": state["topic"],
                        "report": state["report"],
                        "iteration": state["iteration"],
                        "meta": state["meta"]
                    }
                    await self.bus.publish("stream:critic", critic_input)
                    await self.bus.acknowledge("stream:synthesizer:completed", group_name, msg_id)
                    
            except Exception as e:
                logger.error(f"[Supervisor] Error in synthesizer response listener: {e}")
                await asyncio.sleep(1.0)

    async def listen_critic(self):
        group_name = "group-supervisor-critic"
        consumer_name = "consumer-supervisor"
        while self.running:
            try:
                messages = await self.bus.read_stream(
                    stream="stream:critic:completed",
                    group=group_name,
                    consumer=consumer_name,
                    count=5,
                    block_ms=1000
                )
                for msg_id, data in messages:
                    report_id = data.get("report_id")
                    state = await self.get_state(report_id)
                    if not state:
                        await self.bus.acknowledge("stream:critic:completed", group_name, msg_id)
                        continue
                    
                    logger.info(f"[Supervisor] [{report_id}] Critic agent finished.")
                    
                    # Update state
                    state["critique"] = data.get("critique", {})
                    state["iteration"] = data.get("iteration", state["iteration"])
                    state["meta"] = data.get("meta", state["meta"])
                    
                    # Routing Decision
                    requires_research = state["critique"].get("requires_research", False)
                    iteration = state["iteration"]
                    
                    if requires_research and iteration < 2:
                        logger.info(f"[Supervisor] [{report_id}] Critique requested re-search. Looping back to Searcher (Next iteration: {iteration})")
                        state["current_stage"] = "searcher"
                        await self.save_state(report_id, state)
                        
                        searcher_input = {
                            "report_id": report_id,
                            "topic": state["topic"],
                            "max_sources": state["max_sources"],
                            "iteration": iteration,
                            "critique": state["critique"],
                            "search_results": state.get("search_results", []),
                            "scraped_documents": state.get("scraped_documents", []),
                            "meta": state["meta"]
                        }
                        await self.bus.publish("stream:searcher", searcher_input)
                    else:
                        logger.info(f"[Supervisor] [{report_id}] Report coverage completed or threshold reached. Finalizing...")
                        state["status"] = "completed"
                        state["end_time"] = time.time()
                        state["meta"]["wall_clock_seconds"] = round(state["end_time"] - state["start_time"], 2)
                        await self.save_state(report_id, state)
                        
                        # Publish complete notification to routes
                        await self.bus.publish("stream:research:finished", {
                            "report_id": report_id,
                            "status": "completed",
                            "state": state
                        })
                        
                    await self.bus.acknowledge("stream:critic:completed", group_name, msg_id)
                    
            except Exception as e:
                logger.error(f"[Supervisor] Error in critic response listener: {e}")
                await asyncio.sleep(1.0)

    async def listen_errors(self):
        group_name = "group-supervisor-errors"
        consumer_name = "consumer-supervisor"
        while self.running:
            try:
                messages = await self.bus.read_stream(
                    stream="stream:supervisor:errors",
                    group=group_name,
                    consumer=consumer_name,
                    count=5,
                    block_ms=1000
                )
                for msg_id, data in messages:
                    report_id = data.get("report_id")
                    agent = data.get("agent")
                    error_msg = data.get("error", "Unknown error")
                    
                    state = await self.get_state(report_id)
                    if not state:
                        await self.bus.acknowledge("stream:supervisor:errors", group_name, msg_id)
                        continue
                    
                    logger.warning(f"[Supervisor] [{report_id}] Error reported by {agent}: {error_msg}")
                    
                    current_stage = state.get("current_stage", "planner")
                    retries = state.get("retries", {})
                    current_retries = retries.get(current_stage, 0)
                    
                    if current_retries < self.retry_limit:
                        # Retry logic: increment and republish
                        retries[current_stage] = current_retries + 1
                        state["retries"] = retries
                        await self.save_state(report_id, state)
                        
                        logger.info(f"[Supervisor] [{report_id}] Retrying stage '{current_stage}' (Attempt {retries[current_stage] + 1})")
                        
                        # Re-publish task depending on active stage
                        if current_stage == "planner":
                            await self.bus.publish("stream:planner", {
                                "report_id": report_id,
                                "topic": state["topic"],
                                "depth": state["depth"],
                                "meta": state["meta"]
                            })
                        elif current_stage == "searcher":
                            await self.bus.publish("stream:searcher", {
                                "report_id": report_id,
                                "topic": state["topic"],
                                "max_sources": state["max_sources"],
                                "iteration": state["iteration"],
                                "critique": state.get("critique", {}),
                                "research_plan": state.get("research_plan", {}),
                                "search_results": state.get("search_results", []),
                                "scraped_documents": state.get("scraped_documents", []),
                                "meta": state["meta"]
                            })
                        elif current_stage == "synthesizer":
                            await self.bus.publish("stream:synthesizer", {
                                "report_id": report_id,
                                "topic": state["topic"],
                                "research_plan": state.get("research_plan", {}),
                                "scraped_documents": state["scraped_documents"],
                                "meta": state["meta"]
                            })
                        elif current_stage == "critic":
                            await self.bus.publish("stream:critic", {
                                "report_id": report_id,
                                "topic": state["topic"],
                                "report": state["report"],
                                "iteration": state["iteration"],
                                "meta": state["meta"]
                            })
                    else:
                        # Retries exceeded: fail the request
                        logger.error(f"[Supervisor] [{report_id}] Exceeded retry limit for stage '{current_stage}'. Failing request.")
                        state["status"] = "failed"
                        state["error"] = f"Agent {agent} failed with: {error_msg}"
                        await self.save_state(report_id, state)
                        
                        await self.bus.publish("stream:research:finished", {
                            "report_id": report_id,
                            "status": "failed",
                            "error": state["error"]
                        })
                        
                    await self.bus.acknowledge("stream:supervisor:errors", group_name, msg_id)
                    
            except Exception as e:
                logger.error(f"[Supervisor] Error in error stream listener: {e}")
                await asyncio.sleep(1.0)

    async def timeout_watcher(self):
        """
        Periodically checks for requests running longer than 5 minutes (300 seconds)
        and forces them into timeout failure state.
        """
        while self.running:
            try:
                # Watcher interval
                await asyncio.sleep(5.0)
                
                now = time.time()
                active_report_ids = []
                
                # Fetch active states depending on message bus
                if isinstance(self.bus, RedisMessageBus):
                    # Find keys in Redis
                    keys = await self.bus.client.keys("research:state:*")
                    for k in keys:
                        report_id = k.split(":")[-1]
                        active_report_ids.append(report_id)
                else:
                    active_report_ids = list(self.states.keys())
                
                for report_id in active_report_ids:
                    state = await self.get_state(report_id)
                    if not state or state.get("status") in ["completed", "failed", "timeout"]:
                        continue
                    
                    elapsed = now - state.get("start_time", now)
                    if elapsed > 300.0:
                        logger.error(f"[Supervisor] [{report_id}] Research run exceeded global 5 minute timeout ({elapsed:.1f}s). Terminating.")
                        
                        state["status"] = "timeout"
                        state["error"] = "Global timeout limit (5 minutes) exceeded."
                        await self.save_state(report_id, state)
                        
                        await self.bus.publish("stream:research:finished", {
                            "report_id": report_id,
                            "status": "timeout",
                            "error": "Global timeout limit (5 minutes) exceeded."
                        })
                        
            except Exception as e:
                logger.error(f"[Supervisor] Error in timeout watcher: {e}")
