"""
FastAPI entry point with lifespan-based startup.
"""
from contextlib import asynccontextmanager
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import SYNC_TICKET_PROCESSING
from .db import init_db
from .seed import seed_all
from .rag.ingest_kbs import ingest_all_kbs
from .routers.auth_router import router as auth_router
from .routers.tickets_router import router as tickets_router, _process_ticket_background
from .routers.personas_router import router as personas_router
from .routers.users_router import router as users_router
from .routers.analytics_router import router as analytics_router


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
            print(f"[Startup] Queued {len(pending)} pending tickets for processing")
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(personas_router)
app.include_router(users_router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
