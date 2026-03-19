# routers/task.py

# ---------------------------
# Standard Library Imports
# ---------------------------
from typing import Annotated, List

# ---------------------------
# FastAPI Imports
# ---------------------------
from fastapi import APIRouter, Depends

# ---------------------------
# Local App Imports
# ---------------------------
from app.schemas.task import TaskCreate, TaskRead, TaskReadExtended, TaskUpdate
from app.schemas.schedule import ScheduleCreate
from app.services.task import TaskService
from app.dependencies.task import get_task_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.care_space_member import CareSpaceMember
from app.repositories.care_space_member import CareSpaceMemberRepository
from app.dependencies.care_space import get_care_space_member_repo
from app.dependencies.auth import get_current_user

from app.core.permissions import ensure_member_and_can_manage_tasks
from app.dependencies.care_space_member import get_current_member
from app.schemas.task import TaskUpdateRequest, TaskDateFilter, TaskPriority, TaskStatus
from app.schemas.task_completion import TaskStatusUpdateRequest

# ---------------------------
# Router Configuration
# ---------------------------
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

# ---------------------------
# Create Task Endpoint
# ---------------------------
@router.post("/", response_model=TaskRead, description="Create a new task with optional assignments and schedules.")
async def create_task(
    task_data: TaskCreate,
    care_space_id: int,
    assigned_user_ids: List[int] = None,
    schedule_data: List[ScheduleCreate] = None,
    member: CareSpaceMember = Depends(get_current_member),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Create a task in the specified care space.

    Permissions:
    - User must be a member of the care space with editor or owner role.
    
    Optional:
    - `assigned_user_ids` to assign task to specific users.
    - `schedule_data` to create task schedules.
    """
    return await task_service.create_task(
        care_space_id=care_space_id,
        task_data=task_data,
        assigned_user_ids=assigned_user_ids,
        schedule_data=schedule_data,
        member=member
    )

# ---------------------------
# List Tasks by Care Space Endpoint
# ---------------------------
@router.get(
    "/care-space/{care_space_id}",
    response_model=List[TaskReadExtended],
    description="Get all tasks under a specific care space, including assignments and schedules."
)
async def list_tasks_by_care_space(
    care_space_id: int,
    member: CareSpaceMember = Depends(get_current_member),  # current user's member info
    task_service: TaskService = Depends(get_task_service)
):
    """
    Retrieve all tasks for a care space.

    Permissions:
    - User must be a member of the care space.
    - Eagerly loads assignments and schedules by default.
    """
    return await task_service.list_tasks_by_care_space(
        care_space_id=care_space_id,
        member=member,
        eager_load=True
    )


# ---------------------------
# GET SINGLE TASK BY ID
# ---------------------------
@router.get(
    "/{task_id}/detail",
    response_model=TaskReadExtended,
    description="Get a single task by ID with full details including assignments and schedules."
)
async def get_task_detail(
    task_id: int,
    member: CareSpaceMember = Depends(get_current_member),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Retrieve a single task with all assignments and schedules.
    Useful for displaying the task details page.
    """
    return await task_service.get_task_full_by_id(
        task_id=task_id,
        member=member
    )


@router.get(
    "/member/{user_id}",  # <-- user ID here, not member ID
    response_model=List[TaskReadExtended]
)
async def list_tasks_by_member(
    user_id: int,  # dynamic user to fetch tasks for
    current_member: CareSpaceMember = Depends(get_current_member),  # current user for permissions
    task_service: TaskService = Depends(get_task_service)
):
    # Optional permission check: ensure the current member can view tasks
    ensure_member_and_can_manage_tasks(current_member)

    return await task_service.list_tasks_by_member(user_id)


@router.get(
    "/me",
    response_model=List[TaskReadExtended],
    summary="List My Tasks",
    description="Get all tasks assigned to the currently logged-in user."
)
async def list_my_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    date_filter: TaskDateFilter = TaskDateFilter.all,
    priority: TaskPriority | None = None,
    status: TaskStatus | None = None,
    task_service: TaskService = Depends(get_task_service)
):
    return await task_service.list_tasks_for_current_user(
        current_user=current_user,
        date_filter=date_filter,
        priority=priority,
        status=status
    )

# ---------------------------
# List Tasks by Creator
# ---------------------------
@router.get(
    "/created/me",
    response_model=List[TaskReadExtended],
    summary="List Tasks Created by Me",
    description="Get all tasks created by the currently logged-in user."
)
async def list_tasks_created_by_me(
    current_user: Annotated[User, Depends(get_current_user)],
    date_filter: TaskDateFilter = TaskDateFilter.all,
    priority: TaskPriority | None = None,
    status: TaskStatus | None = None,
    task_service: TaskService = Depends(get_task_service)
):
    return await task_service.list_tasks_created_by_current_user(
        current_user=current_user,
        date_filter=date_filter,
        priority=priority,
        status=status
    )

# ---------------------------
# Update Task Endpoint
# ---------------------------
@router.put(
    "/{task_id}",
    response_model=TaskReadExtended,
    description="Update an existing task, including assignments and schedules."
)
async def update_task(
    task_id: int,
    data: TaskUpdateRequest,
    member: CareSpaceMember = Depends(get_current_member),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Update a task's fields, assignments, and schedules.
    """

    return await task_service.update_task(
        task_id=task_id,
        updates=data.updates,
        assigned_user_ids=data.assigned_user_ids,
        schedule_data=data.schedule_data,
        member=member
    )


# ---------------------------
# Delete Task Endpoint
# ---------------------------
@router.delete(
    "/{task_id}",
    response_model=dict,
    description="Delete a task and all related assignments, completions, and schedules."
)
async def delete_task(
    task_id: int,
    member: CareSpaceMember = Depends(get_current_member),
    task_service: TaskService = Depends(get_task_service)
):
    """
    Delete a task by ID.

    Permissions:
    - Only a care space member with appropriate permissions can delete tasks.
    
    Returns:
    - {"deleted": True} if task was successfully deleted
    - {"deleted": False} if task not found
    """
    deleted = await task_service.delete_task(task_id=task_id, member=member)
    return {"deleted": deleted}
    

@router.patch(
    "/update-status",
    summary="Update task completion or acknowledge assignment",
    description="Mark a task as completed/missed/pending or acknowledge assignment."
)
async def update_task_status(
    data: TaskStatusUpdateRequest,
    member: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service)

):
    """
    Dynamic endpoint to handle:
    - Task acknowledgment (`acknowledged_at`)
    - Completion updates (`completed`, `missed`, `pending`)
    - Undo completion by setting status='pending'
    """
    return await task_service.update_task_status(data)