from typing import Dict, Any, List, Optional
from app.search.bm25 import get_bm25_index
from app.search.scraper import Scraper
from app.search.ranking import rank_and_deduplicate
from app.utils.logger import logger
from app.utils.timer import async_timer
from app.agents.base import BaseWorkerAgent
from app.utils.message_bus import MessageBus

class SearcherAgent(BaseWorkerAgent):
    """
    Searcher Agent Worker process.
    Reads sub-queries, executes BM25 search on the local index, scrapes/normalizes content,
    and publishes results to search completed stream.
    """
    def __init__(self, concurrency_limit: int = 10, bus: Optional[MessageBus] = None):
        super().__init__(
            agent_name="SearcherAgent",
            input_stream="stream:searcher",
            output_stream="stream:searcher:completed",
            concurrency_limit=concurrency_limit,
            bus=bus
        )

    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        iteration = message_data.get("iteration", 0)
        topic = message_data.get("topic", "")
        max_sources = message_data.get("max_sources", 20)
        
        # Determine active queries based on iteration
        active_queries = []
        if iteration == 0:
            plan = message_data.get("research_plan", {})
            active_queries = plan.get("queries", [])
            logger.info(f"[Searcher Worker] Running initial search. Queries: {active_queries}")
        else:
            critique = message_data.get("critique", {})
            active_queries = critique.get("gaps", [])
            if not active_queries:
                active_queries = [f"{topic} gaps"]
            logger.info(f"[Searcher Worker] Running iteration {iteration} search. Queries: {active_queries}")
            
        if not active_queries:
            logger.warning("[Searcher Worker] No queries found. Defaulting to searching the topic.")
            active_queries = [topic]

        client_index = get_bm25_index()
        raw_query_results = []
        
        async with async_timer() as t:
            for query in active_queries:
                logger.debug(f"[Searcher Worker] Searching for: '{query}'")
                matches = client_index.search(query, top_k=max_sources * 2)
                
                query_docs = []
                for doc_idx, score in matches:
                    doc = client_index.documents[doc_idx]
                    query_docs.append({
                        "url": doc.get("url"),
                        "title": doc.get("title"),
                        "snippet": doc.get("snippet", ""),
                        "content": doc.get("content", ""),
                        "score": score
                    })
                raw_query_results.append(query_docs)
                
            # Merge and deduplicate results
            top_docs = rank_and_deduplicate(raw_query_results, max_sources)
            
            # Scrape and normalize documents
            search_results = []
            scraped_documents = []
            
            for i, doc in enumerate(top_docs):
                source_id = f"S{i+1}"
                search_results.append({
                    "source_id": source_id,
                    "url": doc["url"],
                    "title": doc["title"],
                    "snippet": doc["snippet"],
                    "score": round(doc["score"], 4)
                })
                
                normalized = Scraper.scrape(doc)
                scraped_documents.append({
                    "source_id": source_id,
                    "url": normalized["url"],
                    "title": normalized["title"],
                    "content": normalized["content"],
                    "timestamp": normalized["timestamp"]
                })

        # If subsequent iteration, merge with existing results
        if iteration > 0:
            prev_search_results = message_data.get("search_results", [])
            prev_scraped_documents = message_data.get("scraped_documents", [])
            
            combined_raw = []
            for ps, pd in zip(prev_search_results, prev_scraped_documents):
                combined_raw.append({
                    "url": ps["url"],
                    "title": ps["title"],
                    "snippet": ps["snippet"],
                    "content": pd["content"],
                    "score": ps["score"]
                })
            for ns, nd in zip(search_results, scraped_documents):
                combined_raw.append({
                    "url": ns["url"],
                    "title": ns["title"],
                    "snippet": ns["snippet"],
                    "content": nd["content"],
                    "score": ns["score"]
                })
                
            final_top = rank_and_deduplicate([combined_raw], max_sources)
            
            search_results = []
            scraped_documents = []
            for i, doc in enumerate(final_top):
                source_id = f"S{i+1}"
                search_results.append({
                    "source_id": source_id,
                    "url": doc["url"],
                    "title": doc["title"],
                    "snippet": doc.get("snippet", ""),
                    "score": round(doc["score"], 4)
                })
                
                if "timestamp" in doc:
                    scraped_documents.append({
                        "source_id": source_id,
                        "url": doc["url"],
                        "title": doc["title"],
                        "content": doc["content"],
                        "timestamp": doc["timestamp"]
                    })
                else:
                    normalized = Scraper.scrape(doc)
                    scraped_documents.append({
                        "source_id": source_id,
                        "url": normalized["url"],
                        "title": normalized["title"],
                        "content": normalized["content"],
                        "timestamp": normalized["timestamp"]
                    })

        logger.info(
            f"[Searcher Worker] Finished. Gathered and normalized {len(scraped_documents)} documents. "
            f"Execution time: {t['elapsed']:.2f} seconds."
        )
        
        meta = message_data.get("meta", {})
        interactions = meta.get("agent_interactions", 0) + 1
        meta["agent_interactions"] = interactions
        meta["searcher_duration"] = meta.get("searcher_duration", 0.0) + t["elapsed"]
        
        return {
            "search_results": search_results,
            "scraped_documents": scraped_documents,
            "meta": meta
        }


# Keep compatibility for existing imports
async def run_searcher(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback LangGraph node for the Searcher Agent.
    """
    agent = SearcherAgent()
    return await agent.process_message(state)
