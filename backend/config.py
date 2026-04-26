import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()

# LLM (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.2

# RAG (BM25 — no vector DB or embedding model needed)
KB_NAMESPACES = {
    "billing": str(BASE_DIR / "data" / "billing_kb"),
    "technical": str(BASE_DIR / "data" / "technical_kb"),
    "refund": str(BASE_DIR / "data" / "refund_kb"),
}
CHUNK_WORDS = 300       # approximate words per KB chunk
CHUNK_OVERLAP_WORDS = 30
RETRIEVAL_TOP_K = 5
FEW_SHOT_TOP_K = 3
CLASSIFICATION_MIN_CONFIDENCE = 0.6

# Persistence — use /tmp on Vercel (writable), local dir otherwise
_IS_VERCEL = bool(os.environ.get("VERCEL"))
_db_dir = "/tmp" if _IS_VERCEL else str(BASE_DIR)
SQLITE_PATH = os.environ.get("SQLITE_PATH", str(Path(_db_dir) / "support_triage.db"))

# Auth
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 60 * 8  # 8 hours

# SLA targets in hours per category
SLA_TARGETS_HOURS = {
    "billing": 4,
    "technical": 8,
    "refund": 24,
    "other": 24,
}

# On Vercel, process tickets synchronously inside the request (no background threads).
# Locally, background threads are used so the POST returns instantly.
SYNC_TICKET_PROCESSING = _IS_VERCEL or bool(os.environ.get("SYNC_TICKET_PROCESSING"))

# Groq free-tier pacing: 2 LLM calls/ticket, ~30 RPM limit.
# Only applied during batch startup requeue, not per-request.
GROQ_INTER_CALL_DELAY_SEC = float(os.environ.get("GROQ_INTER_CALL_DELAY_SEC", "5"))

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not set. Get a free key at https://console.groq.com "
        "and add to backend/.env as GROQ_API_KEY=gsk_..."
    )
