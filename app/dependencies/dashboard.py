# dependencies/task.py

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import Depends

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------
# Local App Imports
# ---------------------------
from app.core.database import get_session
from app.repositories.dashboard import DashboardRepository
from app.services.dashboard import DashboardService
from app.dependencies.care_space_member import get_care_space_member_service
from app.dependencies.task import get_task_repo, get_task_assignment_repo, get_task_completion_repo
from app.repositories.task import TaskRepository
from app.repositories.task_assignment import TaskAssignmentRepository
from app.repositories.task_completion import TaskCompletionRepository

from app.services.care_space_member import CareSpaceMemberService

# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_dashboard_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> DashboardRepository:
    """Provide a DashboardRepository instance using the current DB session."""
    return DashboardRepository(session)



# ---------------------------
# Service Dependency
# ---------------------------

async def get_dashboard_service(
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    assignment_repo: Annotated[TaskAssignmentRepository, Depends(get_task_assignment_repo)],
    completion_repo: Annotated[TaskCompletionRepository, Depends(get_task_completion_repo)],
    care_space_member_service: Annotated[CareSpaceMemberService, Depends(get_care_space_member_service)]
) -> DashboardService:
    """
    Provide a DashboardService instance with the required repositories/services injected.
    """
    return DashboardService(
        task_repo=task_repo,
        assignment_repo=assignment_repo,
        completion_repo=completion_repo,
        care_space_member_service=care_space_member_service
    )