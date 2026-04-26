"""
SQLite database via SQLAlchemy ORM. Five tables:
- users:        authenticated accounts with role + assigned_category
- tickets:      the ticket queue and current state
- feedback_log: audit log of every approve/edit/reject (few-shot source)
- personas:     per-category prompt templates, editable by Senior+ users
- audit_log:    who did what when (login, override, persona edit, user create)
"""
from sqlalchemy import (
    Column, String, Float, DateTime, Text, Integer, Boolean,
    create_engine, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from .config import SQLITE_PATH

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "specialist" | "senior" | "admin"
    assigned_category = Column(String, nullable=True)  # "billing" | "technical" | "refund" | None
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)


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
    # Pipeline output
    classification_json = Column(Text, nullable=True)
    draft_json = Column(Text, nullable=True)
    citations_json = Column(Text, nullable=True)
    # Resolution tracking (for TAT/SLA)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    resolution_action = Column(String, nullable=True)  # "approved" | "edited" | "rejected"
    final_response = Column(Text, nullable=True)


class FeedbackLogModel(Base):
    """Records every human action on a ticket draft. Source for few-shot retrieval."""
    __tablename__ = "feedback_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    action = Column(String, nullable=False)  # "approved" | "edited" | "rejected"
    original_draft = Column(Text, nullable=False)
    final_response = Column(Text, nullable=True)
    edit_distance = Column(Float, nullable=True)  # 0.0-1.0 normalized
    ticket_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PersonaModel(Base):
    """Per-category prompt template. Editable by Senior+ users without redeploy."""
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, unique=True, nullable=False)  # "billing" | "technical" | "refund"
    prompt_template = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    version = Column(Integer, default=1)


class AuditLogModel(Base):
    """Generic audit trail."""
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # "login" | "override" | "persona_edit" | "user_create"
    target_type = Column(String, nullable=True)  # "ticket" | "persona" | "user"
    target_id = Column(String, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


engine = create_engine(f"sqlite:///{SQLITE_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()
