"""
Few-shot memory using BM25 text search.
Approved/edited responses are stored as text in feedback_log.
At query time we build a BM25 index over the stored ticket messages
and return the top-k most lexically similar examples.
No embedding model or binary blobs required.
"""
import re
from rank_bm25 import BM25Okapi
from .config import FEW_SHOT_TOP_K
from .db import get_session, FeedbackLogModel


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def store_feedback_embedding(log_id: int, ticket_message: str, final_response: str, category: str):
    """No-op: BM25 queries the DB text directly — nothing extra to store."""
    pass


def get_few_shot_examples(
    ticket_message: str, category: str, top_k: int = FEW_SHOT_TOP_K
) -> list[dict]:
    session = get_session()
    try:
        records = (
            session.query(FeedbackLogModel)
            .filter(
                FeedbackLogModel.category == category,
                FeedbackLogModel.action.in_(["approved", "edited"]),
                FeedbackLogModel.final_response.isnot(None),
            )
            .all()
        )
    finally:
        session.close()

    if not records:
        return []

    corpus = [_tokenize(r.ticket_message) for r in records]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize(ticket_message))
    ranked = sorted(zip(scores, records), reverse=True)[:top_k]
    return [
        {
            "ticket_message": r.ticket_message,
            "final_response": r.final_response,
            "similarity": round(float(s), 4),
        }
        for s, r in ranked
    ]
