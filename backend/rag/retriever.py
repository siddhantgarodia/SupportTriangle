"""
BM25-based KB retrieval. No vector store, no embedding model.
Queries the in-memory indexes built by ingest_kbs.ingest_all_kbs().
"""
from rag.ingest_kbs import _indexes, _tokenize
from config import RETRIEVAL_TOP_K


def retrieve_kb_context(
    query: str, namespace: str, top_k: int = RETRIEVAL_TOP_K
) -> list[dict]:
    data = _indexes.get(namespace)
    if not data:
        return []

    tokens = _tokenize(query)
    scores = data["bm25"].get_scores(tokens)
    ranked = sorted(zip(scores, data["chunks"]), reverse=True)[:top_k]
    return [
        {
            "chunk_id": c["chunk_id"],
            "content": c["content"],
            "source_file": c["source_file"],
            "score": round(float(s), 4),
        }
        for s, c in ranked
        if s > 0
    ]
