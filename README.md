# SupportTriangle

An AI-powered customer support triage system. Incoming tickets are automatically classified, routed to a category-specific specialist agent, and a draft response is generated using RAG over a knowledge base and few-shot examples from past approved responses. Human agents review, approve, edit, or reject each draft before it is sent.

---

## How it works

```
Ticket submitted
      │
      ▼
 Supervisor agent
 (Groq llama-3.3-70b)
 Classifies → billing | technical | refund | other
      │
      ├─ confidence < 0.6 → Fallback (human review)
      │
      ▼
 Few-shot retrieval
 (top-3 past approved responses for this category)
      │
      ▼
 Specialist agent
 (Groq llama-3.3-70b + RAG over KB + few-shot block)
 Produces: response_text, cited_chunk_ids, confidence, suggested_action
      │
      ▼
 Human agent reviews draft
 Approve → sent as-is
 Edit    → modified draft sent, edit distance recorded
 Reject  → escalated for manual handling
      │
      ▼
 Feedback stored as embedding
 (improves future few-shot examples automatically)
```

---

## Project structure

```
SupportTriangle/
├── backend/                   # FastAPI Python backend
│   ├── main.py                # App entry point, lifespan startup, CORS
│   ├── config.py              # All constants: LLM model, SLA targets, JWT config
│   ├── db.py                  # SQLAlchemy ORM — 5 tables
│   ├── auth.py                # JWT issuance/validation, role guards
│   ├── seed.py                # Idempotent seed: 5 users, 3 personas, 15 tickets
│   ├── analytics.py           # TAT, SLA breach, approval rate, agent leaderboard
│   ├── graph.py               # LangGraph pipeline (supervisor → specialist/fallback)
│   ├── few_shot.py            # Embedding store + cosine retrieval for few-shot
│   │
│   ├── agents/
│   │   ├── supervisor.py      # Classifies ticket → category + confidence
│   │   ├── specialist.py      # Unified specialist: loads persona from DB, calls Groq
│   │   └── fallback.py        # Returns escalation draft when confidence is low
│   │
│   ├── rag/
│   │   ├── ingest_kbs.py      # Chunks KB markdown files → ChromaDB collections
│   │   └── retriever.py       # Semantic search over KB namespace, returns top-k chunks
│   │
│   ├── routers/
│   │   ├── auth_router.py     # POST /auth/login, GET /auth/me
│   │   ├── tickets_router.py  # Ticket CRUD + approve/edit/reject/requeue
│   │   ├── personas_router.py # GET/PUT persona prompt templates
│   │   ├── users_router.py    # Admin user management
│   │   └── analytics_router.py# GET /analytics?window=today|week|month|all
│   │
│   ├── schemas/
│   │   ├── user.py            # User, UserCreate, UserLogin, TokenResponse
│   │   ├── ticket.py          # Ticket, TicketClassification, TicketCreateRequest
│   │   ├── persona.py         # Persona, PersonaUpdate
│   │   ├── response.py        # DraftResponse, KBCitation, DraftWithCitations
│   │   └── analytics.py       # KPIBundle, TimeSeriesPoint, CategoryBreakdown, AgentStats
│   │
│   ├── prompts/
│   │   ├── classify.txt       # System prompt for supervisor classification
│   │   └── personas/
│   │       ├── billing_default.txt
│   │       ├── technical_default.txt
│   │       └── refund_default.txt
│   │
│   ├── data/
│   │   ├── billing_kb/        # Markdown knowledge base files for billing
│   │   ├── technical_kb/      # Markdown knowledge base files for technical
│   │   ├── refund_kb/         # Markdown knowledge base files for refund
│   │   └── sample_tickets.json# 15 seed tickets for demo
│   │
│   ├── requirements.txt
│   └── .env                   # GROQ_API_KEY, JWT_SECRET
│
└── frontend/                  # React + Vite frontend
    ├── vite.config.js          # Dev server on :5173, proxies /api → :8000
    ├── src/
    │   ├── main.jsx            # React root
    │   ├── App.jsx             # React Router v6 routes, role-gated
    │   ├── auth.js             # localStorage token helpers
    │   ├── api.js              # Axios instance with JWT interceptor + named exports
    │   │
    │   ├── hooks/
    │   │   └── useAuth.js      # login(), logout(), current user state
    │   │
    │   ├── routes/
    │   │   ├── LoginPage.jsx   # Email/password login form
    │   │   ├── TicketsPage.jsx # Three-panel ticket triage UI
    │   │   ├── AnalyticsPage.jsx# KPI cards + charts (senior/admin only)
    │   │   ├── PersonasPage.jsx # Live persona editor (senior/admin only)
    │   │   └── UsersPage.jsx   # User management table (admin only)
    │   │
    │   └── components/
    │       ├── AppLayout.jsx       # Sidebar + main content wrapper
    │       ├── Sidebar.jsx         # Nav links filtered by role
    │       ├── ProtectedRoute.jsx  # Redirects unauthenticated / unauthorized users
    │       ├── TicketQueue.jsx     # Scrollable ticket list with status/category badges
    │       ├── TicketDetail.jsx    # Full ticket info panel
    │       ├── DraftReviewPanel.jsx# AI draft with approve/edit/reject controls
    │       ├── KBCitations.jsx     # Expandable KB source citations
    │       ├── NewTicketModal.jsx  # Form to submit a new ticket
    │       ├── KPICard.jsx         # Single metric card
    │       ├── TimeSeriesChart.jsx # Recharts line chart (ticket volume)
    │       ├── CategoryBarChart.jsx# Recharts bar chart (category + SLA breaches)
    │       └── AgentLeaderboard.jsx# Table of agent performance metrics
    └── package.json
```

---

## Database schema

Five SQLite tables managed by SQLAlchemy:

| Table | Purpose |
|---|---|
| `users` | Authenticated accounts with role and assigned category |
| `tickets` | Incoming tickets with pipeline output and resolution state |
| `feedback_log` | Every agent action (approve/edit/reject) with edit distance and embedding |
| `personas` | Per-category prompt templates, editable at runtime |
| `audit_log` | Immutable trail of logins, overrides, and persona edits |

---

## Roles and access

| Role | Tickets | Analytics | Personas | Users |
|---|---|---|---|---|
| `specialist` | Own category only | — | — | — |
| `senior` | All categories | Read | Edit | — |
| `admin` | All categories | Read | Edit | Full CRUD |

Specialists are assigned a single category (`billing`, `technical`, or `refund`). Their ticket queue is filtered to show only tickets classified in that category plus any unclassified ones.

---

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | — | Returns JWT token |
| GET | `/auth/me` | Any | Current user profile |
| GET | `/tickets` | specialist+ | List tickets (role-scoped) |
| POST | `/tickets` | specialist+ | Create and queue a ticket |
| GET | `/tickets/{id}` | specialist+ | Get single ticket |
| GET | `/tickets/{id}/citations` | specialist+ | KB sources used in draft |
| POST | `/tickets/{id}/approve` | specialist+ | Approve draft as-is |
| POST | `/tickets/{id}/edit` | specialist+ | Send edited draft |
| POST | `/tickets/{id}/reject` | specialist+ | Reject draft for manual handling |
| POST | `/tickets/{id}/requeue` | senior+ | Re-run AI pipeline on a failed ticket |
| POST | `/tickets/requeue-errors` | senior+ | Bulk requeue all errored tickets |
| GET | `/personas` | senior+ | List all persona templates |
| GET | `/personas/{category}` | senior+ | Get one persona |
| PUT | `/personas/{category}` | senior+ | Update persona prompt (takes effect immediately) |
| GET | `/users` | admin | List users |
| POST | `/users` | admin | Create user |
| PATCH | `/users/{id}` | admin | Toggle active / change role |
| GET | `/analytics` | senior+ | KPIs, time series, category breakdown, leaderboard |
| GET | `/health` | — | Health check |

---

## Key technical decisions

**Groq + llama-3.3-70b-versatile** — used for both classification and specialist response drafting. Two LLM calls per ticket; a 5-second inter-call delay respects the free-tier rate limit (30 RPM).

**LangGraph pipeline** — `supervisor → fetch_few_shot → [route] → specialist/fallback → END`. State is a typed dict passed through each node. The graph is compiled once and reused.

**RAG with ChromaDB** — knowledge base markdown files are chunked (400 tokens, 40 overlap) and embedded with `sentence-transformers/all-MiniLM-L6-v2` at startup. Each category has its own ChromaDB collection (`kb_billing`, `kb_technical`, `kb_refund`).

**Few-shot memory** — every approved or edited response is stored with a sentence-transformer embedding of the ticket message. At inference time the top-3 most similar past examples are injected into the specialist prompt, making the system improve over time without retraining.

**Persona-as-config** — prompt templates live in the `personas` database table, not in files. Senior users can edit them via the UI and the next LLM call uses the updated template with no restart required.

**Background processing** — ticket AI pipeline runs in a `threading.Thread(daemon=True)` so POST `/tickets` returns immediately. The frontend polls every 8 seconds until status becomes `draft_ready`.

**JWT authentication** — tokens carry `user_id`, `role`, and `assigned_category`. Expiry is 8 hours. Role enforcement is done at the FastAPI dependency layer via `require_role()` factories.

**Edit distance** — when an agent edits a draft, the normalized Levenshtein ratio between the original draft and the final response is stored as a float (0.0 = no change, 1.0 = complete rewrite). This feeds into the analytics leaderboard.

---

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
echo "GROQ_API_KEY=your_key_here" > .env
echo "JWT_SECRET=change-this-in-production" >> .env

# Run (seeds DB and ingests KBs automatically on first start)
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000` so no CORS configuration is needed during development.

### Demo accounts (seeded automatically)

| Email | Password | Role | Category |
|---|---|---|---|
| admin@supporttriangle.com | admin123 | admin | — |
| senior@supporttriangle.com | senior123 | senior | — |
| billing@supporttriangle.com | billing123 | specialist | billing |
| technical@supporttriangle.com | technical123 | specialist | technical |
| refund@supporttriangle.com | refund123 | specialist | refund |

---

## Configuration reference

All values are in [backend/config.py](backend/config.py).

| Variable | Default | Description |
|---|---|---|
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Groq model for classification and drafting |
| `LLM_TEMPERATURE` | `0.2` | Lower = more deterministic responses |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformer for KB and few-shot embeddings |
| `RETRIEVAL_TOP_K` | `5` | KB chunks injected into each specialist prompt |
| `FEW_SHOT_TOP_K` | `3` | Past approved examples injected into each specialist prompt |
| `CLASSIFICATION_MIN_CONFIDENCE` | `0.6` | Below this threshold the ticket goes to fallback |
| `SLA_TARGETS_HOURS` | billing: 4h, technical: 8h, refund: 24h | SLA breach threshold per category |
| `JWT_EXPIRY_MINUTES` | `480` (8 hours) | JWT token lifetime |
| `GROQ_INTER_CALL_DELAY_SEC` | `5` | Pause between LLM calls to respect free-tier rate limit |
