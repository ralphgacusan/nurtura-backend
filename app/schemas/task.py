"""
schemas/task.py

Pydantic schemas for Task operations.

Features:
- Base task schema
- Task creation schema
- Task read schema
- Task update schema
- Supports priority enum
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime

# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, Field
from typing import Annotated

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.task import TaskPriority
from app.schemas.schedule import ScheduleCreate
from app.schemas.task_completion import TaskCompletionRead

# ---------------------------
# BASE TASK SCHEMA
# ---------------------------
class TaskBase(BaseModel):
    """
    Base schema shared by task creation, read, and update schemas.

    Attributes:
        title (str): Task title (1-100 chars)
        description (str | None): Optional description
        care_space_id (int): Care space ID
        assigned_by (int): User who created task
        due_date (datetime): Due date/time
        priority (TaskPriority | None): Optional priority
    """

    title: Annotated[
        str,
        Field(min_length=1, max_length=100, strip_whitespace=True)
    ]

    description: Annotated[
        str | None,
        Field(max_length=1000)
    ] = None

    due_date: datetime

    priority: TaskPriority | None = None


# ---------------------------
# TASK CREATE SCHEMA
# ---------------------------
class TaskCreate(TaskBase):
    """
    Schema for creating a task.
    """
    pass


# ---------------------------
# TASK READ SCHEMA
# ---------------------------
class TaskRead(TaskBase):
    """
    Schema for reading task data.

    Attributes:
        task_id (int)
        created_at (datetime)
        updated_at (datetime)
    """

    task_id: int
    created_at: datetime
    updated_at: datetime

    assigned_by: int


    model_config = {
        "from_attributes": True
    }

# ---------------------------
# TASK ASSIGNMENT READ SCHEMA
# ---------------------------
class TaskAssignmentRead(BaseModel):
    assignment_id: int
    task_id: int
    assigned_to: int
    acknowledged_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------
# TASK SCHEDULE READ SCHEMA
# ---------------------------
class TaskScheduleRead(BaseModel):
    schedule_id: int
    task_id: int
    start_time: datetime
    end_time: datetime
    recurrence_type: str
    recurrence_days: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------
# EXTENDED TASK READ SCHEMA
# ---------------------------
class TaskReadExtended(TaskRead):
    """
    Extended TaskRead schema to include assignments, schedules, and completions.
    """
    assignments: list[TaskAssignmentRead] = []
    schedules: list[TaskScheduleRead] = []
    completions: list[TaskCompletionRead] = []  # <-- new field for task completions


# ---------------------------
# TASK UPDATE SCHEMA
# ---------------------------
class TaskUpdate(BaseModel):
    """
    Schema for updating a task (PATCH).

    All fields optional.
    """

    title: Annotated[
        str | None,
        Field(min_length=1, max_length=100, strip_whitespace=True)
    ] = None

    description: Annotated[
        str | None,
        Field(max_length=1000)
    ] = None

    due_date: datetime | None = None

    priority: TaskPriority | None = None

class TaskUpdateRequest(BaseModel):
    """
    Full update payload for task.

    Allows updating:
    - task fields
    - assignments
    - schedules
    """

    updates: TaskUpdate

    assigned_user_ids: list[int] | None = None

    schedule_data: list[ScheduleCreate] | None = None


# ---------------------------
# TASK COMPLETION READ SCHEMA
# ---------------------------
class TaskCompletionRead(BaseModel):
    """
    Represents a task completion by an assigned user.
    """
    completion_id: int
    task_id: int
    user_id: int
    status: str  # 'completed', 'missed', 'pending'
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
