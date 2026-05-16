from fastapi import APIRouter, Depends, Query
from auth import require_senior_or_above
from schemas.user import User
from schemas.analytics import AnalyticsResponse
from analytics import get_full_analytics, Window

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    window: Window = Query("week"),
    current_user: User = Depends(require_senior_or_above),
):
    return get_full_analytics(window)
