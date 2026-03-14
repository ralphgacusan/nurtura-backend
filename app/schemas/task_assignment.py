"""
schemas/task_assignment.py

Pydantic schemas for TaskAssignment operations.

Features:
- Base assignment schema
- Assignment creation schema
- Assignment read schema
- Assignment update schema
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
# BASE ASSIGNMENT SCHEMA
# ---------------------------
class TaskAssignmentBase(BaseModel):
    """
    Base schema shared by assignment creation, read, and update.

    Attributes:
        task_id (int): Task ID
        assigned_to (int): User assigned to task
        acknowledged_at (datetime | None): When task was viewed
    """

    task_id: int

    assigned_to: int

    acknowledged_at: datetime | None = None


# ---------------------------
# CREATE SCHEMA
# ---------------------------
class TaskAssignmentCreate(TaskAssignmentBase):
    """
    Schema for creating assignment.
    """
    pass


# ---------------------------
# READ SCHEMA
# ---------------------------
class TaskAssignmentRead(TaskAssignmentBase):
    """
    Schema for reading assignment data.

    Attributes:
        assignment_id (int)
        created_at (datetime)
        updated_at (datetime)
    """

    assignment_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


# ---------------------------
# UPDATE SCHEMA
# ---------------------------
class TaskAssignmentUpdate(BaseModel):
    """
    Schema for updating assignment.

    All fields optional.
    """

    acknowledged_at: datetime | None = None