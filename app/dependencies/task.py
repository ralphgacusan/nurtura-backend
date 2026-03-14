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
from app.repositories.task import TaskRepository
from app.repositories.task_assignment import TaskAssignmentRepository
from app.repositories.schedule import ScheduleRepository
from app.repositories.task_completion import TaskCompletionRepository
from app.services.task import TaskService
from app.services.care_space_member import CareSpaceMemberService
from app.dependencies.care_space_member import get_care_space_member_service


# ---------------------------
# Repository Dependencies
# ---------------------------
async def get_task_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> TaskRepository:
    """Provide a TaskRepository instance using the current DB session."""
    return TaskRepository(session)


async def get_task_assignment_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> TaskAssignmentRepository:
    """Provide a TaskAssignmentRepository instance using the current DB session."""
    return TaskAssignmentRepository(session)


async def get_schedule_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> ScheduleRepository:
    """Provide a ScheduleRepository instance using the current DB session."""
    return ScheduleRepository(session)


async def get_task_completion_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> TaskCompletionRepository:
    """Provide a TaskCompletionRepository instance using the current DB session."""
    return TaskCompletionRepository(session)



# ---------------------------
# Service Dependency
# ---------------------------

async def get_task_service(
    task_repo: Annotated[TaskRepository, Depends(get_task_repo)],
    assignment_repo: Annotated[TaskAssignmentRepository, Depends(get_task_assignment_repo)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repo)],
    completion_repo: Annotated[TaskCompletionRepository, Depends(get_task_completion_repo)],
    care_space_member_service: Annotated[CareSpaceMemberService, Depends(get_care_space_member_service)],
) -> TaskService:
    """
    Provide a TaskService instance with all required repositories injected.
    """
    return TaskService(
        task_repo=task_repo,
        assignment_repo=assignment_repo,
        schedule_repo=schedule_repo,
        completion_repo=completion_repo,
        care_space_member_service=care_space_member_service
    )