import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()

# LLM (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
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
JWT_SECRET = os.getenv("JWT_SECRET", "").strip()
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 60 * 8  # 8 hours

# CORS — on Vercel the frontend and backend share the same origin so "*" is safe;
# override with a comma-separated list via ALLOWED_ORIGINS for stricter control.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",")]

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

CONFIG_ERROR: Optional[str] = None

if not GROQ_API_KEY:
    CONFIG_ERROR = (
        "GROQ_API_KEY is not set. Add it in the Vercel dashboard under "
        "Settings → Environment Variables."
    )
elif not JWT_SECRET or len(JWT_SECRET) < 32:
    CONFIG_ERROR = (
        "JWT_SECRET is not set or is shorter than 32 characters. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )
