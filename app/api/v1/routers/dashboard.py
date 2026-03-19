# app/routers/dashboard.py

from fastapi import APIRouter, Depends
from app.services.dashboard import DashboardService
from app.repositories.dashboard import DashboardRepository
from app.dependencies.auth import get_current_user
from app.dependencies.dashboard import get_dashboard_service
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
async def get_dashboard_summary(
    filter: str = "today",
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get dynamic dashboard summary metrics for the current user.
    Supports filters: today, week, month.
    """

    # Note: DashboardService.get_user_dashboard now expects current_user, not user_id
    summary = await dashboard_service.get_user_dashboard(
        current_user=current_user,
        filter=filter
    )

    return summary