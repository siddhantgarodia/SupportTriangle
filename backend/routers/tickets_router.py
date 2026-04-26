"""
Ticket queue with role-scoped visibility and background AI pipeline processing.
"""
import json
import uuid
import threading
import time
from datetime import datetime
from difflib import SequenceMatcher
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from ..db import TicketModel, FeedbackLogModel, AuditLogModel, get_session
from ..auth import get_current_user, require_specialist_or_above, require_senior_or_above
from ..schemas.user import User
from ..schemas.ticket import Ticket, TicketClassification, TicketCreateRequest, TicketActionRequest
from ..schemas.response import DraftResponse, KBCitation, DraftWithCitations
from ..config import GROQ_INTER_CALL_DELAY_SEC, SYNC_TICKET_PROCESSING
from ..graph import run_triage_pipeline
from ..few_shot import store_feedback_embedding

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _row_to_ticket(t: TicketModel) -> Ticket:
    classification = None
    if t.classification_json:
        try:
            cls_data = json.loads(t.classification_json)
            classification = TicketClassification(**cls_data)
        except Exception:
            pass

    draft = None
    if t.draft_json:
        try:
            draft = DraftResponse(**json.loads(t.draft_json))
        except Exception:
            pass

    return Ticket(
        id=t.id,
        customer_name=t.customer_name,
        customer_email=t.customer_email,
        subject=t.subject,
        message=t.message,
        created_at=t.created_at,
        priority=t.priority,
        status=t.status,
        classification=classification,
        draft=draft,
        resolved_at=t.resolved_at,
        resolved_by_user_id=t.resolved_by_user_id,
        resolution_action=t.resolution_action,
    )


def _normalized_edit_distance(a: str, b: str) -> float:
    if not a and not b:
        return 0.0
    if not a or not b:
        return 1.0
    ratio = SequenceMatcher(None, a, b).ratio()
    return round(1.0 - ratio, 4)


def _process_ticket_background(ticket_id: str, delay: bool = True):
    if delay:
        time.sleep(GROQ_INTER_CALL_DELAY_SEC)
    session = get_session()
    try:
        t = session.query(TicketModel).filter_by(id=ticket_id).first()
        if not t:
            return

        from ..schemas.ticket import Ticket as TicketSchema
        ticket_obj = TicketSchema(
            id=t.id,
            customer_name=t.customer_name,
            customer_email=t.customer_email,
            subject=t.subject,
            message=t.message,
            created_at=t.created_at,
            priority=t.priority,
            status=t.status,
        )

        try:
            classification, draft_with_citations = run_triage_pipeline(ticket_obj)
        except Exception as e:
            print(f"[Tickets] Pipeline error for {ticket_id}: {e}")
            t.status = "error"
            session.commit()
            return

        t.status = "draft_ready"
        if classification:
            t.classification_json = json.dumps(classification.model_dump())
            if classification.suggested_priority:
                t.priority = classification.suggested_priority

        if draft_with_citations:
            t.draft_json = json.dumps(draft_with_citations.draft.model_dump())
            t.citations_json = json.dumps([c.model_dump() for c in draft_with_citations.citations])

        session.commit()
        print(f"[Tickets] Pipeline done for {ticket_id}")
    except Exception as e:
        print(f"[Tickets] Background error for {ticket_id}: {e}")
    finally:
        session.close()


@router.get("", response_model=list[Ticket])
def list_tickets(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_specialist_or_above),
):
    session = get_session()
    try:
        q = session.query(TicketModel)
        if current_user.role == "specialist" and current_user.assigned_category:
            cat = current_user.assigned_category
            q = q.filter(
                TicketModel.classification_json.like(f'%"category": "{cat}"%') |
                TicketModel.classification_json.like(f'%"category":"{cat}"%') |
                TicketModel.status.in_(["new", "processing"])
            )
        if status:
            q = q.filter(TicketModel.status == status)
        tickets = q.order_by(TicketModel.created_at.desc()).all()
        return [_row_to_ticket(t) for t in tickets]
    finally:
        session.close()


@router.post("", response_model=Ticket, status_code=201)
def create_ticket(
    body: TicketCreateRequest,
    current_user: User = Depends(require_specialist_or_above),
):
    session = get_session()
    try:
        ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        row = TicketModel(
            id=ticket_id,
            customer_name=body.customer_name,
            customer_email=body.customer_email,
            subject=body.subject,
            message=body.message,
            priority=body.priority,
            status="processing",
            created_at=datetime.utcnow(),
        )
        session.add(row)
        session.commit()

        if SYNC_TICKET_PROCESSING:
            _process_ticket_background(ticket_id, delay=False)
            session.expire_all()
            row = session.query(TicketModel).filter_by(id=ticket_id).first()
        else:
            threading.Thread(
                target=_process_ticket_background,
                args=(ticket_id,),
                daemon=True,
            ).start()

        return _row_to_ticket(row)
    finally:
        session.close()


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(
    ticket_id: str,
    current_user: User = Depends(require_specialist_or_above),
):
    session = get_session()
    try:
        t = session.query(TicketModel).filter_by(id=ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return _row_to_ticket(t)
    finally:
        session.close()


@router.get("/{ticket_id}/citations", response_model=list[KBCitation])
def get_citations(
    ticket_id: str,
    current_user: User = Depends(require_specialist_or_above),
):
    session = get_session()
    try:
        t = session.query(TicketModel).filter_by(id=ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if not t.citations_json:
            return []
        return [KBCitation(**c) for c in json.loads(t.citations_json)]
    finally:
        session.close()


@router.post("/{ticket_id}/approve", response_model=Ticket)
def approve_ticket(
    ticket_id: str,
    current_user: User = Depends(require_specialist_or_above),
):
    session = get_session()
    try:
        t = session.query(TicketModel).filter_by(id=ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if t.status != "draft_ready":
            raise HTTPException(status_code=400, detail=f"Ticket is not in draft_ready state (current: {t.status})")

        original_draft = ""
        if t.draft_json:
            try:
                original_draft = json.loads(t.draft_json).get("response_text", "")
            except Exception:
                pass

        t.status = "approved"
        t.resolved_at = datetime.utcnow()
        t.resolved_by_user_id = current_user.id
        t.resolution_action = "approved"
        t.final_response = original_draft

        category = "other"
        if t.classification_json:
            try:
                category = json.loads(t.classification_json).get("category", "other")
            except Exception:
                pass

        log = FeedbackLogModel(
            ticket_id=t.id,
            user_id=current_user.id,
            category=category,
            action="approved",
            original_draft=original_draft,
            final_response=original_draft,
            edit_distance=0.0,
            ticket_message=t.message,
        )
        session.add(log)
        session.add(AuditLogModel(
            user_id=current_user.id,
            action="override",
            target_type="ticket",
            target_id=ticket_id,
            metadata_json=json.dumps({"resolution": "approved"}),
        ))
        session.commit()

        threading.Thread(
            target=store_feedback_embedding,
            args=(log.id, t.message, original_draft, category),
            daemon=True,
        ).start()

        return _row_to_ticket(t)
    finally:
        session.close()


@router.post("/{ticket_id}/edit", response_model=Ticket)
def edit_ticket(
    ticket_id: str,
    body: TicketActionRequest,
    current_user: User = Depends(require_specialist_or_above),
):
    session = get_session()
    try:
        t = session.query(TicketModel).filter_by(id=ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if t.status != "draft_ready":
            raise HTTPException(status_code=400, detail=f"Ticket is not in draft_ready state (current: {t.status})")
        if not body.final_response:
            raise HTTPException(status_code=400, detail="final_response is required for edit")

        original_draft = ""
        if t.draft_json:
            try:
                original_draft = json.loads(t.draft_json).get("response_text", "")
            except Exception:
                pass

        edit_dist = _normalized_edit_distance(original_draft, body.final_response)

        t.status = "edited_sent"
        t.resolved_at = datetime.utcnow()
        t.resolved_by_user_id = current_user.id
        t.resolution_action = "edited"
        t.final_response = body.final_response

        category = "other"
        if t.classification_json:
            try:
                category = json.loads(t.classification_json).get("category", "other")
            except Exception:
                pass

        log = FeedbackLogModel(
            ticket_id=t.id,
            user_id=current_user.id,
            category=category,
            action="edited",
            original_draft=original_draft,
            final_response=body.final_response,
            edit_distance=edit_dist,
            ticket_message=t.message,
        )
        session.add(log)
        session.add(AuditLogModel(
            user_id=current_user.id,
            action="override",
            target_type="ticket",
            target_id=ticket_id,
            metadata_json=json.dumps({"resolution": "edited", "edit_distance": edit_dist}),
        ))
        session.commit()

        threading.Thread(
            target=store_feedback_embedding,
            args=(log.id, t.message, body.final_response, category),
            daemon=True,
        ).start()

        return _row_to_ticket(t)
    finally:
        session.close()


@router.post("/{ticket_id}/reject", response_model=Ticket)
def reject_ticket(
    ticket_id: str,
    body: TicketActionRequest,
    current_user: User = Depends(require_specialist_or_above),
):
    session = get_session()
    try:
        t = session.query(TicketModel).filter_by(id=ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if t.status != "draft_ready":
            raise HTTPException(status_code=400, detail=f"Ticket is not in draft_ready state (current: {t.status})")

        original_draft = ""
        if t.draft_json:
            try:
                original_draft = json.loads(t.draft_json).get("response_text", "")
            except Exception:
                pass

        t.status = "rejected"
        t.resolved_at = datetime.utcnow()
        t.resolved_by_user_id = current_user.id
        t.resolution_action = "rejected"

        category = "other"
        if t.classification_json:
            try:
                category = json.loads(t.classification_json).get("category", "other")
            except Exception:
                pass

        log = FeedbackLogModel(
            ticket_id=t.id,
            user_id=current_user.id,
            category=category,
            action="rejected",
            original_draft=original_draft,
            final_response=None,
            edit_distance=None,
            ticket_message=t.message,
        )
        session.add(log)
        session.add(AuditLogModel(
            user_id=current_user.id,
            action="override",
            target_type="ticket",
            target_id=ticket_id,
            metadata_json=json.dumps({"resolution": "rejected", "reason": body.rejection_reason}),
        ))
        session.commit()
        return _row_to_ticket(t)
    finally:
        session.close()


@router.post("/{ticket_id}/requeue", response_model=Ticket)
def requeue_ticket(
    ticket_id: str,
    current_user: User = Depends(require_senior_or_above),
):
    """Re-run the AI pipeline on a ticket that errored."""
    session = get_session()
    try:
        t = session.query(TicketModel).filter_by(id=ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        t.status = "processing"
        session.commit()
        if SYNC_TICKET_PROCESSING:
            _process_ticket_background(ticket_id, delay=False)
            session.expire_all()
            t = session.query(TicketModel).filter_by(id=ticket_id).first()
        else:
            threading.Thread(
                target=_process_ticket_background,
                args=(ticket_id,),
                daemon=True,
            ).start()
        return _row_to_ticket(t)
    finally:
        session.close()


@router.post("/requeue-errors", response_model=dict)
def requeue_all_errors(
    current_user: User = Depends(require_senior_or_above),
):
    """Reset all errored tickets and requeue for AI processing."""
    session = get_session()
    try:
        errored = session.query(TicketModel).filter(TicketModel.status == "error").all()
        for t in errored:
            t.status = "processing"
        session.commit()
        for t in errored:
            if SYNC_TICKET_PROCESSING:
                _process_ticket_background(t.id, delay=False)
            else:
                threading.Thread(
                    target=_process_ticket_background,
                    args=(t.id,),
                    daemon=True,
                ).start()
        return {"requeued": len(errored)}
    finally:
        session.close()
