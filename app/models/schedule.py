"""
models/schedule.py

Defines the Schedule SQLAlchemy model.
Schedules define when a task should occur, including start time,
end time, and optional recurrence settings.

Fields:
- schedule_id: Primary key.
- task_id: FK to tasks.
- start_time: Start datetime.
- end_time: End datetime.
- recurrence_type: Recurrence type enum.
- recurrence_days: Optional bitmask for selected weekdays.
- created_at: Timestamp of creation.

Relationships:
- task: Many-to-one with Task.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone
import enum

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


# ---------------------------
# Schedule Enums
# ---------------------------
class RecurrenceType(str, enum.Enum):
    """Recurrence type of the schedule."""
    none = "none"
    daily = "daily"
    custom = "custom"


# ---------------------------
# Schedule Model
# ---------------------------
class Schedule(Base):
    """
    SQLAlchemy model representing a task schedule.

    Attributes:
        schedule_id (int): Primary key.
        task_id (int): Linked task.
        start_time (datetime): Start datetime.
        end_time (datetime): End datetime.
        recurrence_type (RecurrenceType): Recurrence type.
        recurrence_days (int | None): Bitmask for weekdays.
        created_at (datetime): Creation timestamp.
        task (Task): Related task.
    """

    __tablename__ = "schedules"

    # ---------------------------
    # Columns
    # ---------------------------
    schedule_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key for schedule"
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.task_id"),
        nullable=False,
        doc="FK to tasks"
    )

    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="Start datetime"
    )

    end_time = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="End datetime"
    )

    recurrence_type = Column(
        Enum(RecurrenceType),
        nullable=False,
        default=RecurrenceType.none,
        doc="Type of recurrence"
    )

    recurrence_days = Column(
        Integer,
        nullable=True,
        doc="Bitmask for weekdays"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        doc="Creation timestamp"
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    task = relationship(
        "Task",
        back_populates="schedules",
        doc="Many-to-one relationship to task"
    )