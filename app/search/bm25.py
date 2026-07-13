import math
import re
from typing import List, Dict, Any, Tuple
from app.utils.logger import logger

class BM25Index:
    """
    A pure Python implementation of the BM25 ranking algorithm.
    Optimized for memory efficiency and portable across environments.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[Dict[str, Any]] = []
        self.doc_lens: List[int] = []
        self.avgdl: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.tf: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}

    def fit(self, documents: List[Dict[str, Any]]):
        """
        Fits the BM25 index on a set of document objects.
        """
        logger.info(f"Fitting BM25 index on {len(documents)} documents...")
        self.documents = documents
        self.doc_lens = []
        self.tf = []
        self.doc_freqs = {}
        
        for idx, doc in enumerate(documents):
            # Combine fields to build search index text
            text = f"{doc.get('title', '')} {doc.get('snippet', '')} {doc.get('content', '')}"
            tokens = self.tokenize(text)
            self.doc_lens.append(len(tokens))
            
            # Document Term Frequencies
            doc_tf = {}
            for token in tokens:
                doc_tf[token] = doc_tf.get(token, 0) + 1
            self.tf.append(doc_tf)
            
            # Global Document Frequencies
            for token in doc_tf.keys():
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1
                
        self.avgdl = sum(self.doc_lens) / len(documents) if documents else 0.0
        
        # Calculate IDF scores
        N = len(documents)
        for term, df in self.doc_freqs.items():
            # BM25 smoothed IDF formula
            self.idf[term] = math.log(1 + (N - df + 0.5) / (df + 0.5))
            
        logger.info(f"BM25 index training complete. Average document length: {self.avgdl:.2f} tokens. Vocabulary size: {len(self.idf)}")

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenizes text by stripping HTML tags, lowercasing, and pulling out word boundaries.
        """
        # Clean HTML tags
        cleaned_text = re.sub(r'<[^>]*>', ' ', text.lower())
        # Capture words with alphanumeric characters
        return re.findall(r'\b[a-z0-9]+\b', cleaned_text)

    def search(self, query: str, top_k: int = 20) -> List[Tuple[int, float]]:
        """
        Scores all documents against a query string using the BM25 algorithm.
        Returns a sorted list of tuples (document_index, bm25_score).
        """
        query_tokens = self.tokenize(query)
        scores = []
        
        for idx, doc_tf in enumerate(self.tf):
            score = 0.0
            doc_len = self.doc_lens[idx]
            for token in query_tokens:
                if token in doc_tf:
                    tf = doc_tf[token]
                    idf = self.idf.get(token, 0.0)
                    # BM25 formulation
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                    score += idf * (numerator / denominator)
            scores.append((idx, score))
            
        # Sort documents by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

# Global singleton instance of BM25 index
_global_index = None

def get_bm25_index() -> BM25Index:
    """
    Retrieves or initializes the global singleton BM25Index.
    Pre-loads documents.json from the configured dataset directory.
    """
    global _global_index
    if _global_index is None:
        import json
        from pathlib import Path
        from app.utils.config import settings
        
        _global_index = BM25Index()
        doc_path = Path(settings.data_dir) / "documents.json"
        
        if doc_path.exists():
            logger.info(f"Loading document collection from {doc_path} for indexing...")
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                _global_index.fit(docs)
            except Exception as e:
                logger.error(f"Failed to parse documents.json: {e}")
                raise
        else:
            logger.warning(f"Document collection not found at {doc_path}. Starting with empty index.")
            
    return _global_index

