"""
FastAPI entry point with lifespan-based startup.
"""
from collections import defaultdict
from contextlib import asynccontextmanager
import threading
import time
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .logging_config import setup_logging
from .config import SYNC_TICKET_PROCESSING, ALLOWED_ORIGINS, CONFIG_ERROR
from .db import init_db
from .seed import seed_all
from .rag.ingest_kbs import ingest_all_kbs
from .routers.auth_router import router as auth_router
from .routers.tickets_router import router as tickets_router, _process_ticket_background
from .routers.personas_router import router as personas_router
from .routers.users_router import router as users_router
from .routers.analytics_router import router as analytics_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def _requeue_pending():
    """Process any tickets left in 'new' or 'processing' state from a prior run."""
    from .db import get_session, TicketModel
    time.sleep(2)
    session = get_session()
    try:
        pending = session.query(TicketModel).filter(
            TicketModel.status.in_(["new", "processing"])
        ).all()
        for t in pending:
            t.status = "processing"
        session.commit()
        for t in pending:
            threading.Thread(
                target=_process_ticket_background,
                args=(t.id,),
                daemon=True,
            ).start()
        if pending:
            logger.info(f"Queued {len(pending)} pending tickets for processing")
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if CONFIG_ERROR:
        logger.error(f"Startup blocked — misconfiguration: {CONFIG_ERROR}")
        yield
        return
    init_db()
    seed_all()
    ingest_all_kbs()
    # On Vercel (serverless), don't spawn background threads — they'll be killed.
    if not SYNC_TICKET_PROCESSING:
        threading.Thread(target=_requeue_pending, daemon=True).start()
    yield


app = FastAPI(
    title="SupportTriangle API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware.
# allow_credentials must be False when allow_origins contains "*" — browsers reject
# the combination. This app uses JWT in the Authorization header, not cookies,
# so credentials=False is correct.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def config_check_middleware(request: Request, call_next):
    if CONFIG_ERROR and request.url.path != "/health":
        return JSONResponse(
            status_code=503,
            content={"detail": f"Server misconfigured: {CONFIG_ERROR}"},
        )
    return await call_next(request)


_rate_limit_store: dict = defaultdict(list)
_RATE_LIMIT_REQUESTS = 100
_RATE_LIMIT_WINDOW = 60  # seconds


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _RATE_LIMIT_WINDOW

    timestamps = [t for t in _rate_limit_store.get(client_ip, []) if t > window_start]
    if len(timestamps) >= _RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
            headers={"Retry-After": str(_RATE_LIMIT_WINDOW)},
        )
    _rate_limit_store[client_ip] = timestamps + [now]
    return await call_next(request)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';"
    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests with tracing ID."""
    request_id = str(uuid.uuid4())
    
    # Log request
    logger.info(
        f"Incoming request: {request.method} {request.url.path}",
        extra={"request_id": request_id},
    )
    
    try:
        response = await call_next(request)
        logger.info(
            f"Response: {response.status_code}",
            extra={"request_id": request_id},
        )
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(
            f"Request failed: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True,
        )
        raise

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(personas_router)
app.include_router(users_router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    if CONFIG_ERROR:
        return JSONResponse(
            status_code=503,
            content={"status": "misconfigured", "error": CONFIG_ERROR},
        )
    return {"status": "ok", "version": "2.0.0"}
