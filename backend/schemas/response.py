"""
Pydantic models for AI-generated draft responses, KB citations, and feedback records.
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional


class DraftResponse(BaseModel):
    response_text: str
    cited_chunk_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_action: Literal["resolve", "escalate", "request_info"]
    tone_notes: Optional[str] = None


class KBCitation(BaseModel):
    chunk_id: str
    content: str
    source_file: str
    namespace: str


class DraftWithCitations(BaseModel):
    draft: DraftResponse
    citations: list[KBCitation]


class FeedbackRecord(BaseModel):
    ticket_id: str
    action: Literal["approved", "edited", "rejected"]
    original_draft: str
    final_response: Optional[str] = None
    edit_distance: Optional[int] = None
    category: str
