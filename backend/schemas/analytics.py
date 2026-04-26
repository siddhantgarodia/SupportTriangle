from pydantic import BaseModel
from typing import Literal


class KPIBundle(BaseModel):
    total_tickets: int
    avg_tat_hours: float
    sla_breach_count: int
    sla_breach_rate: float
    draft_approval_rate: float
    avg_classification_confidence: float
    avg_edit_distance: float


class TimeSeriesPoint(BaseModel):
    timestamp: str
    count: int


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    sla_breach_count: int


class AgentStats(BaseModel):
    user_id: str
    user_email: str
    user_full_name: str
    role: str
    tickets_handled: int
    approval_rate: float
    avg_edit_distance: float


class AnalyticsResponse(BaseModel):
    window: Literal["today", "week", "month", "all"]
    kpis: KPIBundle
    time_series: list[TimeSeriesPoint]
    category_breakdown: list[CategoryBreakdown]
    agent_leaderboard: list[AgentStats]
