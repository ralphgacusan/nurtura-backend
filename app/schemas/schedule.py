"""
schemas/schedule.py

Pydantic schemas for Schedule operations.

Features:
- Base schedule schema
- Schedule creation schema
- Schedule read schema
- Schedule update schema
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
from app.models.schedule import RecurrenceType


# ---------------------------
# BASE SCHEMA
# ---------------------------
class ScheduleBase(BaseModel):
    """
    Base schema shared by schedule create/read/update.

    Attributes:
        task_id (int): Task ID
        start_time (datetime): Start datetime
        end_time (datetime): End datetime
        recurrence_type (RecurrenceType)
        recurrence_days (int | None): Bitmask for weekdays
    """

    start_time: datetime

    end_time: datetime

    recurrence_type: RecurrenceType = RecurrenceType.none

    recurrence_days: int | None = None


# ---------------------------
# CREATE SCHEMA
# ---------------------------
class ScheduleCreate(ScheduleBase):
    """
    Schema for creating schedule.
    """
    pass


# ---------------------------
# READ SCHEMA
# ---------------------------
class ScheduleRead(ScheduleBase):
    """
    Schema for reading schedule.

    Attributes:
        schedule_id (int)
        created_at (datetime)
    """

    schedule_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ---------------------------
# UPDATE SCHEMA
# ---------------------------
class ScheduleUpdate(BaseModel):
    """
    Schema for updating schedule.

    All fields optional.
    """

    start_time: datetime | None = None

    end_time: datetime | None = None

    recurrence_type: RecurrenceType | None = None

    recurrence_days: int | None = None