"""For tickets classified as 'other' or with low confidence."""
from ..schemas.response import DraftResponse, DraftWithCitations


def fallback_draft() -> DraftWithCitations:
    return DraftWithCitations(
        draft=DraftResponse(
            response_text=(
                "This ticket requires human review — the AI was not confident "
                "enough to draft an automated response."
            ),
            cited_chunk_ids=[],
            confidence=0.0,
            suggested_action="escalate",
        ),
        citations=[],
    )
