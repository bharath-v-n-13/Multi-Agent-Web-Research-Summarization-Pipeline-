from app.search.bm25 import BM25Index

def test_bm25_tokenization():
    """
    Verifies tokenization correctly cleans HTML and parses words.
    """
    index = BM25Index()
    text = "<html><body><h1>Quantum Computing</h1><p>Superconducting qubits and error correction.</p></body></html>"
    tokens = index.tokenize(text)
    
    assert "quantum" in tokens
    assert "computing" in tokens
    assert "superconducting" in tokens
    assert "qubits" in tokens
    assert "error" in tokens
    assert "html" not in tokens
    assert "body" not in tokens

def test_bm25_fit_and_search():
    """
    Verifies that documents are matched and ranked correctly based on query terms.
    """
    docs = [
        {
            "url": "http://example.com/1",
            "title": "Quantum Error Correction",
            "snippet": "Exploring surface codes for qubits.",
            "content": "Quantum error correction is a core field in fault tolerance."
        },
        {
            "url": "http://example.com/2",
            "title": "Deep Learning and AI Systems",
            "snippet": "A guide to neural networks and transformers.",
            "content": "Deep learning models are scaling with massive parameter sizes."
        },
        {
            "url": "http://example.com/3",
            "title": "Solar Cells and Green Energy",
            "snippet": "Improving photovoltaic efficiency.",
            "content": "Photovoltaic grid cells generate solar power efficiently."
        }
    ]
    
    index = BM25Index()
    index.fit(docs)
    
    # 1. Search for quantum error correction
    results = index.search("quantum error", top_k=2)
    assert len(results) <= 2
    # Document 1 must be ranked first since it has "quantum" and "error"
    first_doc_idx = results[0][0]
    assert docs[first_doc_idx]["url"] == "http://example.com/1"
    assert results[0][1] > 0.0
    
    # 2. Search for solar cells
    results = index.search("photovoltaic solar", top_k=1)
    assert len(results) == 1
    assert docs[results[0][0]]["url"] == "http://example.com/3"
