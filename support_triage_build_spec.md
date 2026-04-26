# Support Triage Dashboard — Complete Build Specification

> **TO THE AI ASSISTANT (Claude Code / Copilot):** This document is a complete, self-contained build specification. Read it end-to-end before writing any code. Follow the phases in order. At each checkpoint, pause and summarize what you built before proceeding. Do not deviate from the architecture. Ask the user only when explicitly instructed to, or if a dependency install fails.

---

## 0. META-INSTRUCTIONS FOR THE AI

**Your job:** Build a working full-stack application called "Support Triage Dashboard" end-to-end. The user is a beginner; they should be able to run it locally with minimal intervention.

**Operating principles:**
1. **Work in phases.** There are 10 phases. Complete each one fully before moving to the next.
2. **Verify before proceeding.** After each phase, print what was built and ask the user to confirm it works before moving on.
3. **Explain as you go.** For every non-trivial file you create, add a comment block at the top explaining the file's role in plain English.
4. **Prefer simplicity over cleverness.** This project will be defended in an interview by a beginner. Use the most readable approach, not the most sophisticated.
5. **Never fabricate.** If you don't know a package's current API, say so and check. If you're uncertain about version compatibility, use the exact versions in this spec.
6. **Absolute paths.** Always use paths relative to the project root. The root is `support-triage/`.
7. **If the user already built ClaimSense before this, reuse patterns.** The `agents/`, `rag/`, `schemas/` conventions should feel consistent. But this is a separate, standalone project in its own repo.

**Environment assumptions:**
- OS: Windows or macOS or Linux (handle all three)
- Python 3.11 available
- Node.js 20+ available
- Git installed
- User has a free Google AI Studio API key (if missing, instruct them to get one from `aistudio.google.com`)

**What NOT to do:**
- Do not use OpenAI, Anthropic, or any paid LLM APIs — Gemini free tier only.
- Do not add authentication or real user accounts. Assume the "logged in agent" is implicit.
- Do not use Docker, Kubernetes, or any infrastructure beyond local dev + Render/Vercel.
- Do not add features beyond this spec. If the user asks for more, treat as separate requests.
- Do not use deprecated LangChain imports. Use modular imports (`langchain-core`, `langchain-google-genai`, etc.).
- Do not build a ticket-submission form for end-customers — this dashboard is for internal support agents only. Tickets come from a pre-seeded pool.

---

## 1. PROJECT OVERVIEW

**Name:** Support Triage Dashboard
**Tagline:** Multi-agent customer support with human-in-the-loop review and continuous learning

**User persona:** A customer-support agent at an enterprise company. They open the dashboard, see a queue of incoming tickets, and for each one an AI specialist has already drafted a response. The agent reviews, edits or approves, and hits send. Every edit improves the system for next time.

**User-facing flow:**
1. Agent opens dashboard at localhost:5173.
2. Left panel: ticket queue. Each ticket card shows: customer name, subject, AI-classified category badge (Billing / Technical / Refund / Other), priority color, "Draft Ready" or "Processing" badge.
3. Agent clicks a ticket. Middle panel shows full ticket detail: customer info, message, metadata.
4. Right panel shows:
   - Classification result with confidence + reasoning
   - Retrieved KB snippets that informed the draft (expandable, with citation IDs)
   - The drafted response (editable textarea)
   - 3 action buttons: **Approve & Send** / **Edit & Send** / **Reject & Escalate**
5. If agent edits the draft before sending, the edit is saved as a few-shot example and boosts future draft quality for similar tickets.
6. Top bar shows live stats: draft approval rate, avg edit distance, classification confidence trend.

**What it demonstrates (for portfolio / interview):**
- Supervisor-worker multi-agent architecture
- Per-domain specialized RAG (namespaced knowledge bases)
- Few-shot learning loop from human feedback
- Structured LLM outputs with Pydantic validation
- LangGraph conditional routing based on classification
- Full-stack integration (React + FastAPI + SQLite)
- Citation-backed responses for auditability

---

## 2. ARCHITECTURE

```
┌──────────────────────┐
│  React Dashboard     │  Frontend (port 5173)
│  3-panel layout      │
└──────────┬───────────┘
           │ HTTP (JSON)
           ▼
┌─────────────────────────────────────────────┐
│  FastAPI Backend (port 8000)                │
│                                             │
│  ┌────────────────────────────────────────┐ │
│  │      LangGraph Multi-Agent Flow        │ │
│  │                                        │ │
│  │         [Supervisor Agent]             │ │
│  │         Classifies ticket              │ │
│  │              │                         │ │
│  │   ┌──────────┼──────────┬──────────┐   │ │
│  │   ▼          ▼          ▼          ▼   │ │
│  │ Billing   Technical   Refund    Other  │ │
│  │ Agent     Agent       Agent     (human)│ │
│  │   │         │          │                │ │
│  │   ▼         ▼          ▼                │ │
│  │ Billing   Tech       Refund             │ │
│  │ KB (RAG)  KB (RAG)   KB (RAG)           │ │
│  │                                        │ │
│  │  + Few-Shot Memory (from approved      │ │
│  │    edits in SQLite) injected into      │ │
│  │    specialist agent prompts            │ │
│  └────────────────────────────────────────┘ │
│                                             │
│  SQLite: tickets, drafts, feedback,         │
│  few-shot examples with embeddings          │
└─────────────────────────────────────────────┘
```

**Key pattern: Supervisor-Worker**
- Supervisor = classifier only (no KB access, no drafting)
- Workers (specialists) = each has ONE KB namespace + persona
- Routing happens via LangGraph conditional edges after supervisor

---

## 3. TECH STACK (PINNED VERSIONS — DO NOT DEVIATE)

### Backend (`requirements.txt`)
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
langchain==0.3.7
langchain-core==0.3.15
langchain-google-genai==2.0.4
langchain-chroma==0.1.4
langchain-huggingface==0.1.2
langchain-text-splitters==0.3.2
langgraph==0.2.45
chromadb==0.5.18
sentence-transformers==3.2.1
pydantic==2.9.2
python-dotenv==1.0.1
sqlalchemy==2.0.35
numpy==1.26.4
```

### Frontend (`package.json` core deps)
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.7.7"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.3",
    "vite": "^5.4.10",
    "tailwindcss": "^3.4.14",
    "postcss": "^8.4.47",
    "autoprefixer": "^10.4.20"
  }
}
```

---

## 4. FOLDER STRUCTURE (CREATE EXACTLY THIS)

```
support-triage/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── graph.py
│   ├── db.py
│   ├── few_shot.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── ticket.py
│   │   └── response.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── supervisor.py
│   │   ├── billing_agent.py
│   │   ├── technical_agent.py
│   │   └── refund_agent.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest_kbs.py
│   │   └── retriever.py
│   ├── prompts/
│   │   ├── classify.txt
│   │   ├── billing_persona.txt
│   │   ├── technical_persona.txt
│   │   └── refund_persona.txt
│   ├── data/
│   │   ├── billing_kb/             (5-6 markdown files)
│   │   │   ├── billing_faq.md
│   │   │   ├── invoice_process.md
│   │   │   ├── payment_methods.md
│   │   │   ├── subscription_tiers.md
│   │   │   └── refund_timelines.md
│   │   ├── technical_kb/           (5-6 markdown files)
│   │   │   ├── login_issues.md
│   │   │   ├── api_errors.md
│   │   │   ├── performance_guide.md
│   │   │   ├── integration_faq.md
│   │   │   └── known_bugs.md
│   │   ├── refund_kb/              (5-6 markdown files)
│   │   │   ├── refund_policy.md
│   │   │   ├── refund_eligibility.md
│   │   │   ├── partial_refunds.md
│   │   │   ├── dispute_process.md
│   │   │   └── chargeback_guide.md
│   │   └── sample_tickets.json     (15 sample tickets)
│   ├── chroma_db/                   (auto-created)
│   ├── support_triage.db            (SQLite, auto-created)
│   ├── scripts/
│   │   ├── seed_tickets.py
│   │   └── generate_sample_kb.py    (generates KB markdown files)
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── index.css
│   │   └── components/
│   │       ├── TicketQueue.jsx
│   │       ├── TicketDetail.jsx
│   │       ├── DraftReviewPanel.jsx
│   │       ├── KBCitations.jsx
│   │       └── StatsBar.jsx
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
├── .gitignore
├── README.md
└── LICENSE
```

---

## 5. DETAILED COMPONENT SPECIFICATIONS

### 5.1 `backend/schemas/ticket.py`

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

Category = Literal["billing", "technical", "refund", "other"]
Priority = Literal["low", "medium", "high"]
Status = Literal["new", "draft_ready", "approved", "edited_sent", "rejected"]

class Ticket(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    subject: str
    message: str
    created_at: datetime
    priority: Priority = "medium"
    status: Status = "new"
    classification: Optional["TicketClassification"] = None
    draft: Optional["DraftResponse"] = None

class TicketClassification(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    suggested_priority: Priority
```

### 5.2 `backend/schemas/response.py`

```python
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
    final_response: Optional[str] = None  # None if rejected
    edit_distance: Optional[int] = None
    category: str
```

### 5.3 `backend/config.py`

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
LLM_MODEL = "gemini-2.0-flash"
LLM_TEMPERATURE = 0.2
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHROMA_DB_PATH = str(BASE_DIR / "chroma_db")
SQLITE_PATH = str(BASE_DIR / "support_triage.db")

KB_NAMESPACES = {
    "billing": str(BASE_DIR / "data" / "billing_kb"),
    "technical": str(BASE_DIR / "data" / "technical_kb"),
    "refund": str(BASE_DIR / "data" / "refund_kb"),
}

CHUNK_SIZE = 400
CHUNK_OVERLAP = 40
RETRIEVAL_TOP_K = 5
FEW_SHOT_TOP_K = 3

CLASSIFICATION_MIN_CONFIDENCE = 0.6

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY not set. Get one free at https://aistudio.google.com "
        "and add to backend/.env as GOOGLE_API_KEY=..."
    )
```

### 5.4 `backend/db.py`

SQLAlchemy setup for two tables:

```python
"""
SQLite with SQLAlchemy. Two tables:
- tickets: the ticket queue and their current state
- feedback_log: every approval/edit/rejection, including few-shot embeddings
"""
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer, LargeBinary
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
from .config import SQLITE_PATH

Base = declarative_base()

class TicketModel(Base):
    __tablename__ = "tickets"
    id = Column(String, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    priority = Column(String, default="medium")
    status = Column(String, default="new")
    classification_json = Column(Text, nullable=True)  # serialized TicketClassification
    draft_json = Column(Text, nullable=True)           # serialized DraftResponse
    citations_json = Column(Text, nullable=True)       # serialized list[KBCitation]

class FeedbackLogModel(Base):
    __tablename__ = "feedback_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, nullable=False)
    category = Column(String, nullable=False)
    action = Column(String, nullable=False)  # approved/edited/rejected
    original_draft = Column(Text, nullable=False)
    final_response = Column(Text, nullable=True)
    edit_distance = Column(Integer, nullable=True)
    ticket_message = Column(Text, nullable=False)  # needed for few-shot retrieval
    ticket_embedding = Column(LargeBinary, nullable=True)  # numpy array bytes
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(f"sqlite:///{SQLITE_PATH}")
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return SessionLocal()
```

### 5.5 `backend/few_shot.py`

The few-shot retrieval layer — core differentiator.

```python
"""
Few-shot memory: retrieves similar past approved/edited responses to
inject into specialist agent prompts. Uses cosine similarity over
ticket embeddings stored in SQLite.
"""
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from .config import EMBEDDING_MODEL, FEW_SHOT_TOP_K
from .db import get_session, FeedbackLogModel

_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embedder

def embed_text(text: str) -> np.ndarray:
    vec = get_embedder().embed_query(text)
    return np.array(vec, dtype=np.float32)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-10
    return float(np.dot(a, b) / denom)

def store_approved_edit(
    ticket_id: str,
    category: str,
    ticket_message: str,
    original_draft: str,
    final_response: str,
    action: str,  # "approved" or "edited"
    edit_distance: int
):
    """Store a feedback record with embedding for later retrieval."""
    embedding = embed_text(ticket_message)
    session = get_session()
    try:
        rec = FeedbackLogModel(
            ticket_id=ticket_id,
            category=category,
            action=action,
            original_draft=original_draft,
            final_response=final_response,
            edit_distance=edit_distance,
            ticket_message=ticket_message,
            ticket_embedding=embedding.tobytes(),
        )
        session.add(rec)
        session.commit()
    finally:
        session.close()

def store_rejected(ticket_id: str, category: str, ticket_message: str, original_draft: str):
    """Store rejections (no final_response)."""
    session = get_session()
    try:
        rec = FeedbackLogModel(
            ticket_id=ticket_id,
            category=category,
            action="rejected",
            original_draft=original_draft,
            final_response=None,
            edit_distance=None,
            ticket_message=ticket_message,
            ticket_embedding=embed_text(ticket_message).tobytes(),
        )
        session.add(rec)
        session.commit()
    finally:
        session.close()

def get_few_shot_examples(ticket_message: str, category: str, top_k: int = FEW_SHOT_TOP_K) -> list[dict]:
    """
    Retrieve top-k most similar past APPROVED or EDITED responses (not rejections).
    Returns list of {"ticket_message", "final_response", "similarity"}.
    """
    query_vec = embed_text(ticket_message)
    session = get_session()
    try:
        records = session.query(FeedbackLogModel).filter(
            FeedbackLogModel.category == category,
            FeedbackLogModel.action.in_(["approved", "edited"]),
            FeedbackLogModel.final_response.isnot(None),
            FeedbackLogModel.ticket_embedding.isnot(None),
        ).all()
        if not records:
            return []
        scored = []
        for r in records:
            emb = np.frombuffer(r.ticket_embedding, dtype=np.float32)
            sim = cosine_similarity(query_vec, emb)
            scored.append({
                "ticket_message": r.ticket_message,
                "final_response": r.final_response,
                "similarity": sim,
            })
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]
    finally:
        session.close()
```

### 5.6 `backend/rag/ingest_kbs.py`

Ingests each KB namespace as a separate ChromaDB collection.

```python
"""
Ingests each KB namespace (billing / technical / refund) as its own
ChromaDB collection. Run once before server start; idempotent.
"""
# Use langchain_chroma.Chroma
# For each namespace in KB_NAMESPACES:
#   - Load all .md files
#   - Chunk (size=400, overlap=40)
#   - Embed with MiniLM
#   - Store in collection named f"kb_{namespace}"
#   - Metadata per chunk: {"namespace": namespace, "source_file": filename, "chunk_id": f"{filename}-{idx}"}
```

Must return a summary: `{"billing": 42, "technical": 38, "refund": 31}`.

### 5.7 `backend/rag/retriever.py`

```python
def retrieve_kb_context(query: str, namespace: str, top_k: int = RETRIEVAL_TOP_K) -> list[dict]:
    """
    Retrieve top-k chunks from the namespace's collection.
    Returns list of {"chunk_id", "content", "source_file", "score"}.
    """
```

### 5.8 `backend/agents/supervisor.py`

Classifier only. No KB, no drafting.

**Prompt file: `backend/prompts/classify.txt`**
```
You are a support ticket classifier. Classify the following customer ticket
into exactly one category: billing, technical, refund, or other.

Definitions:
- billing: invoices, payment methods, subscription changes, pricing questions,
  unexpected charges (but NOT refund requests)
- technical: login issues, API errors, performance problems, integration
  questions, bug reports
- refund: any request to get money back, cancel subscription with refund,
  dispute a charge, chargeback
- other: anything not matching above, including account deletion, feature
  requests, general questions, complaints without specific ask

Rules:
1. Pick EXACTLY ONE category.
2. If the ticket mentions refund explicitly, prefer "refund" over "billing"
   even if billing is discussed.
3. Set confidence lower (<0.6) if the ticket is ambiguous or touches multiple
   categories.
4. Suggest priority: "high" for production outages, payment failures, angry
   tone; "medium" for standard issues; "low" for general questions.

Examples:
Ticket: "My card was charged twice for last month's subscription."
→ category: billing, confidence: 0.95, priority: high

Ticket: "I want my money back, this product doesn't work."
→ category: refund, confidence: 0.92, priority: high

Ticket: "I can't log in after the update."
→ category: technical, confidence: 0.94, priority: high

Ticket: "How do I change my company name on the invoice?"
→ category: billing, confidence: 0.88, priority: low

Ticket: "Thanks for the great service!"
→ category: other, confidence: 0.85, priority: low

Now classify this ticket:
Subject: {subject}
Message: {message}
```

**Code:**
```python
def classify_ticket(subject: str, message: str) -> TicketClassification:
    """Returns TicketClassification via structured output. Retry once on validation error."""
```

### 5.9 `backend/agents/billing_agent.py` (template for all 3 specialists)

**Prompt file: `backend/prompts/billing_persona.txt`**
```
You are a professional billing specialist for SaaS customer support. Your
voice is: warm, clear, precise about numbers and dates, apologetic when we
made a mistake, firm when policy applies.

Your response should:
1. Acknowledge the customer's issue in one sentence.
2. Answer directly — reference specific policies or facts from the provided
   KB CONTEXT using citation IDs like [chunk_id].
3. Give a concrete next step (what will happen, by when, what they need to do).
4. Close professionally.

CRITICAL RULES:
- ONLY use information present in the KB CONTEXT. If the context doesn't
  contain the answer, say "I'll need to escalate this to a specialist" and
  set suggested_action to "escalate".
- ALWAYS cite your sources using [chunk_id] inline in the response text.
- Keep response under 150 words unless the issue truly requires more detail.
- Match the tone of the FEW-SHOT EXAMPLES — these are responses our senior
  agents actually approved.

KB CONTEXT:
---
{kb_context}
---

FEW-SHOT EXAMPLES (past approved responses for similar tickets):
---
{few_shot_block}
---

CURRENT TICKET:
Customer: {customer_name}
Subject: {subject}
Message: {message}
---

Draft a response.
```

**Code structure (same for all 3 specialists):**
```python
def draft_billing_response(ticket: Ticket, few_shot_examples: list[dict]) -> DraftWithCitations:
    """
    1. Retrieve top 5 KB chunks from 'billing' namespace using ticket.message as query.
    2. Build kb_context string with [chunk_id] labels.
    3. Build few_shot_block from examples.
    4. Format prompt, call LLM with structured output for DraftResponse.
    5. Return DraftWithCitations(draft=..., citations=[KBCitation(...) for each retrieved chunk]).
    """
```

**Repeat identical structure** for `technical_agent.py` and `refund_agent.py` with their own persona files. Keep the code DRY: consider a shared `_draft_with_specialist(namespace, persona_file, ticket, few_shot)` helper.

### 5.10 `backend/graph.py`

LangGraph with supervisor → conditional → specialist.

**State:**
```python
class TriageState(TypedDict):
    ticket_id: str
    subject: str
    message: str
    customer_name: str
    classification: Optional[TicketClassification]
    few_shot_examples: list[dict]
    draft_with_citations: Optional[DraftWithCitations]
    log: list[str]
    error: Optional[str]
```

**Nodes:**
- `supervisor_node`: calls `classify_ticket`, stores in state.
- `fetch_few_shot_node`: calls `get_few_shot_examples` based on classification + message.
- `billing_node`, `technical_node`, `refund_node`: each calls its specialist.
- `fallback_node`: for "other" or low-confidence — returns a stub draft flagging for human handling, no LLM call.

**Conditional router:**
```python
def route_to_specialist(state: TriageState) -> str:
    cls = state["classification"]
    if not cls or cls.confidence < CLASSIFICATION_MIN_CONFIDENCE:
        return "fallback"
    return {"billing": "billing", "technical": "technical",
            "refund": "refund", "other": "fallback"}[cls.category]
```

**Flow:**
```
START → supervisor → fetch_few_shot → [router] → {billing|technical|refund|fallback} → END
```

**Exported:**
```python
def run_triage_pipeline(ticket: Ticket) -> DraftWithCitations:
    """Run the full pipeline for one ticket. Returns the draft + citations."""
```

### 5.11 `backend/main.py`

**Endpoints:**

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | health check |
| GET | `/tickets` | list all tickets, ordered by created_at desc |
| GET | `/tickets/{ticket_id}` | get single ticket with classification + draft |
| POST | `/tickets/{ticket_id}/process` | (re)run pipeline for this ticket, save classification + draft |
| POST | `/tickets/{ticket_id}/approve` | body: `{}`. Mark approved, log to feedback. |
| POST | `/tickets/{ticket_id}/edit-send` | body: `{"final_response": str}`. Save as few-shot example. |
| POST | `/tickets/{ticket_id}/reject` | body: `{"reason": str}`. Log rejection. |
| GET | `/stats` | returns: total, by_status, approval_rate, avg_edit_distance, avg_classification_confidence |
| POST | `/seed` | re-seed sample tickets (dev-only, clears existing) |

**Startup:**
1. `init_db()`
2. Call `ingest_all_kbs()` — idempotent
3. If zero tickets in DB, call `seed_sample_tickets()`
4. Auto-process all tickets with status `new` in background (or on-demand via endpoint — choose background on startup for better demo).

**CORS:** localhost:5173, localhost:3000, production frontend URL via env.

### 5.12 `backend/scripts/seed_tickets.py`

Loads `data/sample_tickets.json` and inserts into DB with status `new`.

**`sample_tickets.json` must contain 15 tickets covering all categories:**
- 4 billing (invoice question, double charge, plan upgrade, tax exemption request)
- 4 technical (login fails, API 500 errors, slow dashboard, integration webhook)
- 4 refund (within window, outside window, partial refund, chargeback threat)
- 3 "other" or ambiguous (feature request, compliment, multi-category mixed)

**Every ticket structure:**
```json
{
  "id": "TCK-0001",
  "customer_name": "Priya Sharma",
  "customer_email": "priya@example.com",
  "subject": "Double charged this month",
  "message": "Hi, I noticed my card was charged twice for my Pro plan this month - once on Apr 1 and again on Apr 15. Can you check and refund the duplicate? My account email is priya@example.com.",
  "created_at": "2026-04-22T10:30:00"
}
```

Tickets should be varied in tone (polite, frustrated, terse, detailed) to stress-test the classifier.

### 5.13 `backend/scripts/generate_sample_kb.py`

Generates the 15-18 markdown KB files (5-6 per namespace) with realistic SaaS-support content.

**Each markdown file structure:**
```markdown
# [Topic Title]

## Overview
[2-3 sentences]

## Details
[bullet points or paragraphs]

## Process Steps
1. ...
2. ...

## Edge Cases
- ...
```

**Example content per namespace:**

**billing_kb/refund_timelines.md** should state: "Standard refunds process in 5-7 business days to the original payment method. Bank transfers may take up to 10 business days. Customers on annual plans receive pro-rated refunds for unused months."

**technical_kb/login_issues.md** should state: "If a user cannot log in after a password reset, instruct them to clear browser cache or try incognito. If MFA fails, verify the time on their device is synced. For SSO errors, check SAML response in browser dev tools."

**refund_kb/refund_policy.md** should state: "Full refunds available within 14 days of purchase. Partial refunds on prorated basis between 14-30 days if unused. No refunds after 30 days except for documented service failures."

Generate enough substantive content per file that retrieval has real chunks to return (aim for 300-500 words per file).

### 5.14 Frontend — Layout

**3-column layout (flex):**
```
┌─────────────────────────────────────────────────────┐
│  StatsBar (top, full-width)                         │
├──────────┬───────────────────┬──────────────────────┤
│          │                   │                      │
│ Ticket   │   Ticket Detail   │  Draft Review Panel  │
│ Queue    │   (message, meta) │  (classification,    │
│ (list)   │                   │   citations, draft,  │
│          │                   │   action buttons)    │
│          │                   │                      │
│ 25%      │      35%          │         40%          │
└──────────┴───────────────────┴──────────────────────┘
```

On mobile (<768px), stack vertically with collapsible sections.

### 5.15 Frontend — `TicketQueue.jsx`

Props: `tickets`, `selectedId`, `onSelect`.

Each ticket card shows:
- Customer name (bold)
- Subject (truncated to 50 chars)
- Category badge (colored): blue=billing, purple=technical, orange=refund, gray=other, white=unclassified
- Priority indicator (dot: red=high, yellow=medium, green=low)
- Status badge: "New" / "Draft Ready" / "Approved" / "Edited" / "Rejected"
- Relative time (e.g., "12m ago")

Clicking selects the ticket. Selected card has a left border accent.

### 5.16 Frontend — `TicketDetail.jsx`

Shows full ticket:
- Customer name + email
- Subject (large)
- Message (full text, preserved line breaks)
- Metadata row: created_at (formatted), priority, status

### 5.17 Frontend — `DraftReviewPanel.jsx`

When no draft ready: show spinner "AI drafting response..."

When draft ready, show:
1. **Classification Result** — category badge + confidence bar + reasoning text (small)
2. **KB Citations section** — collapsible. Shows `KBCitations` component with each retrieved chunk expandable.
3. **Drafted Response** — `<textarea>` pre-filled with draft, editable. Character count below.
4. **Action buttons** (sticky at bottom):
   - `Approve & Send` (green, primary) — only enabled if draft unchanged from original
   - `Edit & Send` (blue) — only enabled if draft has been modified
   - `Reject & Escalate` (red, outline)
5. On action, call API, show toast, auto-select next ticket in queue.

Track whether textarea is modified: store original draft, compare on change.

### 5.18 Frontend — `KBCitations.jsx`

For each citation: a card with chunk_id badge, source_file, and first 200 chars of content (click to expand full).

### 5.19 Frontend — `StatsBar.jsx`

Top bar with 4 stats (updates after every action via refetch):
- Total tickets processed today
- Approval rate % (approved / (approved+edited+rejected))
- Avg classification confidence
- Edit rate (edited / total decisions)

Each stat: big number + small label.

### 5.20 Frontend — `api.js`

```javascript
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function listTickets() { /* GET /tickets */ }
export async function getTicket(id) { /* GET /tickets/{id} */ }
export async function processTicket(id) { /* POST /tickets/{id}/process */ }
export async function approveTicket(id) { /* POST /tickets/{id}/approve */ }
export async function editSendTicket(id, finalResponse) { /* POST .../edit-send */ }
export async function rejectTicket(id, reason) { /* POST .../reject */ }
export async function getStats() { /* GET /stats */ }
```

Use `fetch` with proper error handling; throw on non-2xx with server message.

### 5.21 Styling

Tailwind. Match a clean SaaS admin look:
- White cards on `slate-50` background
- `rounded-xl`, `shadow-sm`
- Category colors: `blue-100/800` (billing), `purple-100/800` (tech), `orange-100/800` (refund), `slate-100/600` (other)
- Priority dots: `red-500` / `amber-400` / `emerald-400`
- Buttons: `blue-600` primary, `emerald-600` approve, `red-500` reject

---

## 6. BUILD PHASES (EXECUTE IN ORDER)

### Phase 1 — Project Scaffolding
1. Create folder structure exactly as specified.
2. Create `.gitignore` (Python, Node, env, chroma_db, *.db, pycache).
3. Create skeleton README.
4. `git init`.
**Checkpoint:** Print tree, confirm.

### Phase 2 — Backend Foundation
1. Create venv.
2. Write `requirements.txt`. Install.
3. Write `config.py`, `schemas/`, `.env.example`.
4. Write `db.py`. Run `init_db()` once to create tables.
**Checkpoint:** `python -c "from backend.db import init_db; init_db(); print('DB created')"` works.

### Phase 3 — Sample Data Generation
1. Write `scripts/generate_sample_kb.py`. Run it — creates 15-18 markdown files.
2. Write `data/sample_tickets.json` with 15 tickets (detailed in 5.12).
3. Write `scripts/seed_tickets.py`. Run it. Verify DB has 15 tickets.
**Checkpoint:** Show user file listing and a SELECT count of tickets.

### Phase 4 — RAG Pipeline
1. Write `rag/ingest_kbs.py`. Run it — creates 3 ChromaDB collections.
2. Write `rag/retriever.py`.
3. Test each namespace with a sample query. Print top-3 results.
**Checkpoint:** User sees relevant chunks returned per namespace.

### Phase 5 — Few-Shot Layer
1. Write `few_shot.py`.
2. Unit test: manually insert 2 fake feedback records, verify retrieval returns them for similar tickets.
**Checkpoint:** Print the 2 retrieved examples with similarity scores.

### Phase 6 — Individual Agents
Build + test each:
1. Supervisor — classify 3 sample tickets from different categories. Print results.
2. Billing specialist — draft response for a billing ticket with empty few-shot. Print draft + citations.
3. Technical specialist — same test.
4. Refund specialist — same test.
**Checkpoint after each:** Print agent output. User confirms quality.

### Phase 7 — LangGraph Orchestration
1. Write `graph.py` with state, nodes, router.
2. Test end-to-end with 3 sample tickets spanning all categories.
3. Test fallback path with an ambiguous ticket.
**Checkpoint:** Print `DraftWithCitations` for each of the 5 test cases.

### Phase 8 — FastAPI Backend
1. Write `main.py` with all 9 endpoints.
2. On startup: init_db, ingest_kbs, seed if empty, background-process new tickets.
3. Start server. Test each endpoint via curl/Postman.
**Checkpoint:** User confirms all endpoints work; `/stats` returns counts.

### Phase 9 — Frontend
1. Vite scaffold + Tailwind + axios.
2. Write `api.js`.
3. Build components in order: StatsBar → TicketQueue → TicketDetail → KBCitations → DraftReviewPanel.
4. Wire `App.jsx` — fetch tickets on mount, select handling, action handling with optimistic updates.
**Checkpoint:** User opens localhost:5173, sees queue, clicks tickets, reviews drafts, approves/edits one, confirms stats update.

### Phase 10 — Polish + README
1. Error states everywhere: network error toasts, loading skeletons, empty states.
2. Final end-to-end test: approve one, edit one, reject one — verify feedback log, verify next similar ticket uses the few-shot example.
3. Write full `README.md` (template in section 8).
**Checkpoint:** User runs full demo flow start-to-finish.

---

## 7. KNOWN GOTCHAS — HANDLE PROACTIVELY

1. **Gemini + Pydantic structured outputs:** Use `llm.with_structured_output(MyModel)`. If you see `ValidationError`, retry once with an error-feedback prompt. Don't parse JSON manually.

2. **ChromaDB multiple collections:** Each namespace is its own `Chroma(persist_directory=..., collection_name="kb_billing")` etc. Don't confuse `persist_directory` (can be shared) with `collection_name` (must be unique).

3. **HuggingFaceEmbeddings first download:** ~80MB. Warn user. Subsequent runs use cache.

4. **LangChain import drift:** Always use:
   - `from langchain_google_genai import ChatGoogleGenerativeAI`
   - `from langchain_chroma import Chroma`
   - `from langchain_huggingface import HuggingFaceEmbeddings`
   - `from langchain_text_splitters import RecursiveCharacterTextSplitter`
   - `from langgraph.graph import StateGraph, END`

5. **SQLAlchemy + SQLite concurrency:** The background startup job processes tickets. Make sure FastAPI endpoints and background job each use their own session (call `get_session()` per request). Don't share session objects across threads.

6. **Background processing on startup:** Use `asyncio.create_task()` in a FastAPI `@app.on_event("startup")` handler, OR process tickets lazily on first GET `/tickets`. Simpler: process synchronously in `seed_tickets.py` right after seeding, so by the time server fully starts, all drafts are ready. Document this choice.

7. **Gemini free tier = 15 RPM:** When processing 15 tickets at seed time, add `time.sleep(4.5)` between LLM calls to stay under limit. Alternatively process on-demand per ticket when first selected — cleaner UX but slower on demo.

8. **Embedding storage in SQLite:** Store numpy array as bytes via `.tobytes()`, retrieve with `np.frombuffer(..., dtype=np.float32)`. Never pickle — it's fragile across Python versions.

9. **Edit distance calculation:** Use `difflib.SequenceMatcher(None, a, b).ratio()` or character-level Levenshtein. Keep simple: `len(edited) - len(original)` is NOT edit distance — don't use it. Use `difflib` for a 0-1 similarity, derive distance as `1 - ratio`.

10. **Frontend-backend CORS on production:** Document clearly. Frontend `VITE_API_BASE` must point to deployed backend URL. Backend CORS must include deployed frontend origin.

11. **Textarea controlled component:** Use `useState` with `onChange`. Store initial draft separately so you can detect "is this modified?".

12. **Citation rendering:** Response text may contain `[chunk_id]` inline. Render these as pill tags linked to the citation card — use a regex `/\[([^\]]+)\]/g` in rendering.

13. **Markdown KB files — front matter NOT needed:** Just plain markdown. Splitter handles headers naturally.

14. **Windows paths:** Use `pathlib.Path` throughout config and ingestion. Never hardcode `/`.

15. **Sample ticket JSON — UTF-8:** Include diverse customer names (Indian, Western, East Asian). Save file as UTF-8, load with `open(..., encoding='utf-8')`.

16. **Sequence of operations for few-shot:** The few-shot loop only activates AFTER the first edit is stored. On the very first ticket, few_shot_examples will be `[]` — make sure the prompt template handles empty few-shot gracefully ("No prior examples available yet.").

---

## 8. README TEMPLATE (FILL AT PHASE 10)

```markdown
# Support Triage Dashboard

**Multi-agent customer support system with human-in-the-loop review and continuous learning**

[![Demo](./docs/demo.gif)](./docs/demo.mp4)

## Overview
A LangGraph-based multi-agent system for enterprise customer support.
Incoming tickets are classified by a supervisor agent, then routed to one
of three specialist agents (Billing, Technical, Refund) — each with its
own RAG-backed knowledge base. Specialists draft cited responses that a
human agent reviews, approves, edits, or rejects. Approved edits become
few-shot examples, continuously improving future drafts.

## Architecture
[insert diagram]

## Key Design Decisions
- **Supervisor-worker pattern** — classification and drafting are decoupled.
  Each specialist has a focused KB and persona, improving response quality
  over a single-prompt generalist.
- **Per-domain namespaced RAG** — billing/technical/refund each have their
  own ChromaDB collection, eliminating cross-domain noise during retrieval.
- **Citation-backed responses** — every response references [chunk_id]
  tags linked to the retrieved KB chunks, enabling auditability.
- **Few-shot learning loop** — human edits are embedded and stored. The
  top-3 most similar past approvals are injected into future prompts,
  lightweight in-context learning from feedback.
- **Confidence-gated fallback** — low-confidence classifications route to
  a human-handling path, never to a specialist that might hallucinate.

## Tech Stack
[list with why]

## Setup
### Prerequisites
- Python 3.11+
- Node.js 20+
- Free Google AI Studio API key: https://aistudio.google.com

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env, add your GOOGLE_API_KEY
python scripts/generate_sample_kb.py
uvicorn main:app --reload
```
First startup ingests KBs (~1 min) and processes 15 seed tickets (~60 sec
due to rate limits). Subsequent starts are instant.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173.

## How Few-Shot Learning Works
1. Every time you "Edit & Send", the final response is stored with an
   embedding of the ticket message.
2. When a new ticket arrives in the same category, the system embeds it
   and retrieves the top-3 most similar past approvals.
3. Those examples are injected into the specialist's prompt, showing the
   LLM the pattern your agents actually approved.
4. Quality improves over time with no training.

## Future Improvements
- Multi-turn conversations (currently single-response)
- Sentiment analysis in classification
- RAGAS-based retrieval quality monitoring
- Role-based access (manager vs agent)
- Bulk actions

## License
MIT
```

---

## 9. FINAL INSTRUCTIONS TO THE AI

1. Read this entire document before starting.
2. Execute phases 1-10 sequentially. After each phase, print a brief summary and confirm with user.
3. Use the prompt templates in this doc verbatim — they're calibrated for Gemini.
4. Prompt template files should be READ from disk at runtime, not hardcoded in agent files. This makes iteration easy.
5. Every agent function must handle LLM failures gracefully — catch exceptions, log, return a safe fallback (e.g., `DraftResponse(response_text="Unable to draft automatically — please handle manually.", confidence=0.0, suggested_action="escalate")`).
6. Background processing of seed tickets should respect the 15 RPM Gemini limit. Sleep between calls. Show progress in logs.
7. When the user runs the demo end-to-end, the flow must be: open dashboard → see 15 tickets with drafts ready → click one → review → edit slightly → approve → click a SIMILAR ticket → see that the new draft incorporates language from the previous edit. This is the "aha moment" to demo in interviews.
8. Deployment is a stretch goal — get local demo working rock-solid first.

**Success criterion:** User can run `uvicorn main:app --reload` + `npm run dev`, see 15 AI-processed tickets in the queue, and perform at least one approve, one edit, one reject action. After editing one ticket, a subsequent similar ticket should visibly benefit from the few-shot example (agent draft adopts the edited response's style/wording).

---

**End of specification. Begin Phase 1.**
