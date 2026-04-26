"""
Idempotent seed script. Safe to run multiple times.
Creates: 5 users, 3 personas, 15 tickets.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

from .db import init_db, get_session, UserModel, PersonaModel, TicketModel
from .auth import hash_password

BASE_DIR = Path(__file__).resolve().parent

SEED_USERS = [
    {
        "id": "user-admin-001",
        "email": "admin@supporttriangle.com",
        "full_name": "Alex Admin",
        "password": "admin123",
        "role": "admin",
        "assigned_category": None,
    },
    {
        "id": "user-senior-001",
        "email": "senior@supporttriangle.com",
        "full_name": "Sam Senior",
        "password": "senior123",
        "role": "senior",
        "assigned_category": None,
    },
    {
        "id": "user-billing-001",
        "email": "billing@supporttriangle.com",
        "full_name": "Beth Billing",
        "password": "billing123",
        "role": "specialist",
        "assigned_category": "billing",
    },
    {
        "id": "user-technical-001",
        "email": "technical@supporttriangle.com",
        "full_name": "Tom Technical",
        "password": "technical123",
        "role": "specialist",
        "assigned_category": "technical",
    },
    {
        "id": "user-refund-001",
        "email": "refund@supporttriangle.com",
        "full_name": "Rita Refund",
        "password": "refund123",
        "role": "specialist",
        "assigned_category": "refund",
    },
]

PERSONA_FILES = {
    "billing": BASE_DIR / "prompts" / "personas" / "billing_default.txt",
    "technical": BASE_DIR / "prompts" / "personas" / "technical_default.txt",
    "refund": BASE_DIR / "prompts" / "personas" / "refund_default.txt",
}


def seed_users(session):
    created = 0
    for u in SEED_USERS:
        existing = session.query(UserModel).filter_by(id=u["id"]).first()
        if existing:
            continue
        session.add(UserModel(
            id=u["id"],
            email=u["email"],
            full_name=u["full_name"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
            assigned_category=u["assigned_category"],
            is_active=True,
            created_at=datetime.utcnow(),
        ))
        created += 1
    session.commit()
    print(f"[Seed] Users: {created} created, {len(SEED_USERS) - created} already existed")


def seed_personas(session):
    created = 0
    for category, path in PERSONA_FILES.items():
        existing = session.query(PersonaModel).filter_by(category=category).first()
        if existing:
            continue
        template = path.read_text()
        session.add(PersonaModel(
            category=category,
            prompt_template=template,
            updated_at=datetime.utcnow(),
            updated_by_user_id=None,
            version=1,
        ))
        created += 1
    session.commit()
    print(f"[Seed] Personas: {created} created, {3 - created} already existed")


def seed_tickets(session):
    sample_path = BASE_DIR / "data" / "sample_tickets.json"
    if not sample_path.exists():
        print("[Seed] sample_tickets.json not found — skipping tickets")
        return

    tickets_data = json.loads(sample_path.read_text())
    created = 0
    for t in tickets_data:
        existing = session.query(TicketModel).filter_by(id=t["id"]).first()
        if existing:
            continue
        created_at = datetime.fromisoformat(t["created_at"]) if "created_at" in t else datetime.utcnow()
        session.add(TicketModel(
            id=t["id"],
            customer_name=t["customer_name"],
            customer_email=t["customer_email"],
            subject=t["subject"],
            message=t["message"],
            created_at=created_at,
            priority=t.get("priority", "medium"),
            status="new",
        ))
        created += 1
    session.commit()
    print(f"[Seed] Tickets: {created} created, {len(tickets_data) - created} already existed")


def seed_all():
    init_db()
    session = get_session()
    try:
        seed_users(session)
        seed_personas(session)
        seed_tickets(session)
        print("[Seed] Done.")
    finally:
        session.close()


if __name__ == "__main__":
    seed_all()
