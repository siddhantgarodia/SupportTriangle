"""
Loads sample_tickets.json and inserts all tickets into the DB with status 'new'.
Run from the backend/ directory: python scripts/seed_tickets.py
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.db import init_db, get_session, TicketModel, FeedbackLogModel

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_tickets.json"


def seed():
    init_db()
    with open(DATA_FILE, encoding="utf-8") as f:
        tickets = json.load(f)

    session = get_session()
    try:
        session.query(TicketModel).delete()
        session.commit()
        for t in tickets:
            created = datetime.fromisoformat(t["created_at"]) if "created_at" in t else datetime.utcnow()
            row = TicketModel(
                id=t["id"],
                customer_name=t["customer_name"],
                customer_email=t["customer_email"],
                subject=t["subject"],
                message=t["message"],
                created_at=created,
                priority=t.get("priority", "medium"),
                status="new",
            )
            session.add(row)
        session.commit()
        count = session.query(TicketModel).count()
        print(f"✓ Seeded {count} tickets")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
