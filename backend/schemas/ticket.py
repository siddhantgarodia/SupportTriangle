from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime

Priority = Literal["low", "medium", "high"]
Status = Literal["new", "processing", "draft_ready", "approved", "edited_sent", "rejected", "error"]
Category = Literal["billing", "technical", "refund", "other"]


class TicketClassification(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    suggested_priority: Priority


class Ticket(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    subject: str
    message: str
    created_at: datetime
    priority: Priority = "medium"
    status: Status = "new"
    classification: Optional[TicketClassification] = None
    draft: Optional["DraftResponse"] = None
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[str] = None
    resolution_action: Optional[str] = None


class TicketCreateRequest(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    customer_email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    priority: Priority = "medium"


class TicketActionRequest(BaseModel):
    final_response: Optional[str] = None
    rejection_reason: Optional[str] = None


from .response import DraftResponse  # noqa: E402
Ticket.model_rebuild()
