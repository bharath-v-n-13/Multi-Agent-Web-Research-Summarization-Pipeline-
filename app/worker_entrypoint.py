import argparse
import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure the root dir is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.logger import logger
from app.utils.message_bus import get_message_bus

async def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Start an agent worker process.")
    parser.add_argument(
        "--agent", 
        type=str, 
        required=True, 
        choices=["planner", "searcher", "synthesizer", "critic", "supervisor"],
        help="The name of the agent worker to run."
    )
    args = parser.parse_args()
    
    logger.info(f"Starting {args.agent} worker...")
    
    # Configure Redis configuration dynamically
    os.environ["USE_REDIS"] = "true"
    
    # Initialize message bus
    bus = get_message_bus()
    
    # Instantiate and run agent
    if args.agent == "planner":
        from app.agents.planner import PlannerAgent
        agent = PlannerAgent(bus=bus)
        await agent.run_forever()
        
    elif args.agent == "searcher":
        # Fit BM25 index on start so it is preloaded in memory
        from app.search.bm25 import get_bm25_index
        try:
            get_bm25_index()
            logger.info("Pre-loaded BM25 index successfully in Searcher worker.")
        except Exception as e:
            logger.critical(f"Failed to fit BM25 index in Searcher worker: {e}")
            
        from app.agents.searcher import SearcherAgent
        agent = SearcherAgent(bus=bus)
        await agent.run_forever()
        
    elif args.agent == "synthesizer":
        from app.agents.synthesizer import SynthesizerAgent
        agent = SynthesizerAgent(bus=bus)
        await agent.run_forever()
        
    elif args.agent == "critic":
        from app.agents.critic import CriticAgent
        agent = CriticAgent(bus=bus)
        await agent.run_forever()
        
    elif args.agent == "supervisor":
        from app.agents.supervisor import SupervisorAgent
        agent = SupervisorAgent(bus=bus)
        await agent.run_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user. Exiting.")
