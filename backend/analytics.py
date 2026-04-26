"""
Analytics queries. Each function takes a time window and returns aggregated stats.
"""
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Literal

from .db import TicketModel, FeedbackLogModel, UserModel, get_session
from .config import SLA_TARGETS_HOURS
from .schemas.analytics import (
    KPIBundle, TimeSeriesPoint, CategoryBreakdown, AgentStats, AnalyticsResponse
)

Window = Literal["today", "week", "month", "all"]


def _window_start(window: Window) -> datetime:
    now = datetime.utcnow()
    if window == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if window == "week":
        return now - timedelta(days=7)
    if window == "month":
        return now - timedelta(days=30)
    return datetime(2000, 1, 1)


def compute_kpis(session, window: Window) -> KPIBundle:
    start = _window_start(window)
    tickets = session.query(TicketModel).filter(TicketModel.created_at >= start).all()
    total = len(tickets)

    if total == 0:
        return KPIBundle(
            total_tickets=0, avg_tat_hours=0.0,
            sla_breach_count=0, sla_breach_rate=0.0,
            draft_approval_rate=0.0, avg_classification_confidence=0.0, avg_edit_distance=0.0,
        )

    resolved = [t for t in tickets if t.resolved_at is not None]
    tats = [(t.resolved_at - t.created_at).total_seconds() / 3600.0 for t in resolved]
    avg_tat = sum(tats) / len(tats) if tats else 0.0

    breach_count = 0
    for t in resolved:
        category = "other"
        if t.classification_json:
            try:
                cls = json.loads(t.classification_json)
                category = cls.get("category", "other")
            except Exception:
                pass
        target = SLA_TARGETS_HOURS.get(category, SLA_TARGETS_HOURS["other"])
        tat_hours = (t.resolved_at - t.created_at).total_seconds() / 3600.0
        if tat_hours > target:
            breach_count += 1
    breach_rate = (breach_count / len(resolved) * 100) if resolved else 0.0

    feedback = session.query(FeedbackLogModel).filter(FeedbackLogModel.created_at >= start).all()
    approved = sum(1 for f in feedback if f.action == "approved")
    total_actions = len(feedback)
    approval_rate = (approved / total_actions * 100) if total_actions else 0.0

    confidences = []
    for t in tickets:
        if t.classification_json:
            try:
                cls = json.loads(t.classification_json)
                confidences.append(cls.get("confidence", 0.0))
            except Exception:
                pass
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    edit_distances = [f.edit_distance for f in feedback if f.edit_distance is not None]
    avg_edit = sum(edit_distances) / len(edit_distances) if edit_distances else 0.0

    return KPIBundle(
        total_tickets=total,
        avg_tat_hours=round(avg_tat, 2),
        sla_breach_count=breach_count,
        sla_breach_rate=round(breach_rate, 1),
        draft_approval_rate=round(approval_rate, 1),
        avg_classification_confidence=round(avg_conf, 3),
        avg_edit_distance=round(avg_edit, 3),
    )


def compute_time_series(session, window: Window) -> list[TimeSeriesPoint]:
    start = _window_start(window)
    tickets = session.query(TicketModel).filter(TicketModel.created_at >= start).all()
    buckets = defaultdict(int)
    for t in tickets:
        bucket = t.created_at.replace(minute=0, second=0, microsecond=0)
        buckets[bucket.isoformat()] += 1
    return [TimeSeriesPoint(timestamp=ts, count=count) for ts, count in sorted(buckets.items())]


def compute_category_breakdown(session, window: Window) -> list[CategoryBreakdown]:
    start = _window_start(window)
    tickets = session.query(TicketModel).filter(TicketModel.created_at >= start).all()
    by_cat = defaultdict(lambda: {"count": 0, "breach_count": 0})
    for t in tickets:
        category = "other"
        if t.classification_json:
            try:
                cls = json.loads(t.classification_json)
                category = cls.get("category", "other")
            except Exception:
                pass
        by_cat[category]["count"] += 1
        if t.resolved_at:
            target = SLA_TARGETS_HOURS.get(category, SLA_TARGETS_HOURS["other"])
            tat_hours = (t.resolved_at - t.created_at).total_seconds() / 3600.0
            if tat_hours > target:
                by_cat[category]["breach_count"] += 1
    return [CategoryBreakdown(category=cat, count=v["count"], sla_breach_count=v["breach_count"]) for cat, v in by_cat.items()]


def compute_agent_leaderboard(session, window: Window) -> list[AgentStats]:
    start = _window_start(window)
    feedback = session.query(FeedbackLogModel).filter(FeedbackLogModel.created_at >= start).all()
    by_user = defaultdict(lambda: {"actions": [], "edit_distances": []})
    for f in feedback:
        by_user[f.user_id]["actions"].append(f.action)
        if f.edit_distance is not None:
            by_user[f.user_id]["edit_distances"].append(f.edit_distance)

    leaderboard = []
    for user_id, data in by_user.items():
        user = session.query(UserModel).filter_by(id=user_id).first()
        if not user:
            continue
        actions = data["actions"]
        approved = sum(1 for a in actions if a == "approved")
        total = len(actions)
        approval_rate = (approved / total * 100) if total else 0.0
        avg_edit = (
            sum(data["edit_distances"]) / len(data["edit_distances"])
            if data["edit_distances"] else 0.0
        )
        leaderboard.append(AgentStats(
            user_id=user.id, user_email=user.email, user_full_name=user.full_name,
            role=user.role, tickets_handled=total,
            approval_rate=round(approval_rate, 1), avg_edit_distance=round(avg_edit, 3),
        ))
    leaderboard.sort(key=lambda x: x.tickets_handled, reverse=True)
    return leaderboard


def get_full_analytics(window: Window) -> AnalyticsResponse:
    session = get_session()
    try:
        return AnalyticsResponse(
            window=window,
            kpis=compute_kpis(session, window),
            time_series=compute_time_series(session, window),
            category_breakdown=compute_category_breakdown(session, window),
            agent_leaderboard=compute_agent_leaderboard(session, window),
        )
    finally:
        session.close()
