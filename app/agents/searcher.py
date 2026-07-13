from typing import Dict, Any, List
from app.search.bm25 import get_bm25_index
from app.search.scraper import Scraper
from app.search.ranking import rank_and_deduplicate
from app.utils.logger import logger
from app.utils.timer import async_timer

async def run_searcher(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph node for the Searcher Agent.
    Searches the BM25 index using the current active queries, deduplicates the results,
    normalizes the contents using the Scraper, and updates the search state.
    """
    iteration = state.get("iteration", 0)
    topic = state.get("topic", "")
    max_sources = state.get("max_sources", 20)
    
    # Determine active queries based on iteration
    active_queries = []
    if iteration == 0:
        plan = state.get("research_plan", {})
        active_queries = plan.get("queries", [])
        logger.info(f"[Searcher Agent] Running initial search. Queries: {active_queries}")
    else:
        critique = state.get("critique", {})
        # Use critic's new queries, falling back to gaps or topic if not present
        active_queries = critique.get("gaps", [])
        if not active_queries:
            active_queries = [f"{topic} gaps"]
        logger.info(f"[Searcher Agent] Running iteration {iteration} search. Queries: {active_queries}")
        
    if not active_queries:
        logger.warning("[Searcher Agent] No queries found. Defaulting to searching the topic.")
        active_queries = [topic]

    client_index = get_bm25_index()
    
    # Accumulate results for each query
    raw_query_results = []
    
    async with async_timer() as t:
        for query in active_queries:
            logger.debug(f"[Searcher Agent] Searching for: '{query}'")
            # Get matches from the BM25 index
            matches = client_index.search(query, top_k=max_sources * 2)
            
            query_docs = []
            for doc_idx, score in matches:
                # Retrieve the original document
                doc = client_index.documents[doc_idx]
                query_docs.append({
                    "url": doc.get("url"),
                    "title": doc.get("title"),
                    "snippet": doc.get("snippet", ""),
                    "content": doc.get("content", ""),
                    "score": score
                })
            raw_query_results.append(query_docs)
            
        # Merge and deduplicate results across queries, retaining the highest relevance scores
        top_docs = rank_and_deduplicate(raw_query_results, max_sources)
        
        # Scrape and normalize the top selected documents
        search_results = []
        scraped_documents = []
        
        for i, doc in enumerate(top_docs):
            source_id = f"S{i+1}"
            
            # Form search result reference
            search_results.append({
                "source_id": source_id,
                "url": doc["url"],
                "title": doc["title"],
                "snippet": doc["snippet"],
                "score": round(doc["score"], 4)
            })
            
            # Scrape and clean full document body
            normalized = Scraper.scrape(doc)
            scraped_documents.append({
                "source_id": source_id,
                "url": normalized["url"],
                "title": normalized["title"],
                "content": normalized["content"],
                "timestamp": normalized["timestamp"]
            })

    # If this is a subsequent iteration, merge with existing results
    if iteration > 0:
        prev_search_results = state.get("search_results", [])
        prev_scraped_documents = state.get("scraped_documents", [])
        
        # Combine previous and new results
        combined_raw = []
        # Convert previous results back to merge format
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
            
        # Deduplicate the merged set
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
            
            # The doc could already be cleaned, check before running scraper
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
        f"[Searcher Agent] Finished. Gathered and normalized {len(scraped_documents)} documents. "
        f"Execution time: {t['elapsed']:.2f} seconds."
    )
    
    # Increment agent interactions count
    meta = state.get("meta", {})
    interactions = meta.get("agent_interactions", 0) + 1
    meta["agent_interactions"] = interactions
    
    # Record searcher duration
    meta["searcher_duration"] = meta.get("searcher_duration", 0.0) + t["elapsed"]
    
    return {
        "search_results": search_results,
        "scraped_documents": scraped_documents,
        "meta": meta
    }
