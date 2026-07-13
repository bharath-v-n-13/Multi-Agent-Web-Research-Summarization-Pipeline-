from typing import List, Dict, Any
from app.utils.logger import logger

def rank_and_deduplicate(search_results_list: List[List[Dict[str, Any]]], max_sources: int) -> List[Dict[str, Any]]:
    """
    Merges lists of document results retrieved across different search queries.
    Removes duplicate documents by keeping the version with the highest BM25 relevance score.
    Returns the top unique documents up to the max_sources limit.
    """
    merged_docs = {}
    
    for results in search_results_list:
        for doc in results:
            url = doc.get("url")
            if not url:
                continue
            
            score = doc.get("score", 0.0)
            
            # If document already seen, keep it only if the new score is higher
            if url not in merged_docs or score > merged_docs[url]["score"]:
                merged_docs[url] = doc
                
    # Sort merged results by BM25 relevance score in descending order
    sorted_docs = sorted(merged_docs.values(), key=lambda x: x["score"], reverse=True)
    
    # Cap at max_sources
    final_docs = sorted_docs[:max_sources]
    
    total_raw = sum(len(r) for r in search_results_list)
    logger.info(f"Deduplication: Merged {total_raw} raw matches to {len(final_docs)} unique documents (max_sources={max_sources})")
    
    return final_docs
