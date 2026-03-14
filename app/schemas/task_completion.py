"""
schemas/task_completion.py

Pydantic schemas for TaskCompletion operations.

Features:
- Base completion schema
- Completion creation schema
- Completion read schema
- Completion update schema
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, date
from enum import Enum
# ---------------------------
# Pydantic Imports
# ---------------------------
from pydantic import BaseModel, Field
from typing import Annotated

# ---------------------------
# Local App Imports
# ---------------------------
from app.models.task_completion import CompletionStatus


# ---------------------------
# BASE SCHEMA
# ---------------------------
class TaskCompletionBase(BaseModel):
    """
    Base schema shared by create/read/update.

    Attributes:
        task_assignment_id (int)
        scheduled_date (date)
        status (CompletionStatus)
        completed_at (datetime | None)
    """

    task_assignment_id: int

    scheduled_date: date

    status: CompletionStatus

    completed_at: datetime | None = None


# ---------------------------
# CREATE SCHEMA
# ---------------------------
class TaskCompletionCreate(TaskCompletionBase):
    """
    Schema for creating completion.
    """
    pass


# ---------------------------
# READ SCHEMA
# ---------------------------
class TaskCompletionRead(TaskCompletionBase):
    """
    Schema for reading completion.

    Attributes:
        completion_id (int)
    """

    completion_id: int

    model_config = {
        "from_attributes": True
    }


# ---------------------------
# UPDATE SCHEMA
# ---------------------------
class TaskCompletionUpdate(BaseModel):
    """
    Schema for updating completion.

    All fields optional.
    """

    status: CompletionStatus | None = None

    completed_at: datetime | None = None


class CompletionStatus(str, Enum):
    completed = "completed"
    missed = "missed"
    pending = "pending"

class TaskStatusUpdateRequest(BaseModel):
    assignment_id: int | None = None
    completion_id: int | None = None
    status: CompletionStatus | None = None
    acknowledge: bool = False