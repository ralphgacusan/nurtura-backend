"""
models/task_completion.py

Defines the TaskCompletion SQLAlchemy model.
Task completions store the result of a scheduled task occurrence,
including status and completion timestamp.

Fields:
- completion_id: Primary key.
- task_assignment_id: FK to task_assignments.
- scheduled_date: Date of the occurrence.
- status: Completion status enum.
- completed_at: Optional completion timestamp.

Relationships:
- assignment: Many-to-one with TaskAssignment.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone, date
import enum

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, DateTime, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


# ---------------------------
# TaskCompletion Enums
# ---------------------------
class CompletionStatus(str, enum.Enum):
    """Status of task completion."""
    completed = "completed"
    missed = "missed"
    pending = "pending"


# ---------------------------
# TaskCompletion Model
# ---------------------------
class TaskCompletion(Base):
    """
    SQLAlchemy model representing completion of a task occurrence.

    Attributes:
        completion_id (int): Primary key.
        task_assignment_id (int): Linked assignment.
        scheduled_date (date): Date of occurrence.
        status (CompletionStatus): Completion status.
        completed_at (datetime | None): Completion timestamp.
        assignment (TaskAssignment): Related assignment.
    """

    __tablename__ = "task_completions"

    # ---------------------------
    # Columns
    # ---------------------------
    completion_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key for completion"
    )

    task_assignment_id = Column(
        Integer,
        ForeignKey("task_assignments.assignment_id"),
        nullable=False,
        doc="FK to task_assignments"
    )

    scheduled_date = Column(
        Date,
        nullable=False,
        doc="Date of occurrence"
    )

    status = Column(
        Enum(CompletionStatus),
        nullable=False,
        doc="Completion status"
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Completion timestamp"
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    assignment = relationship(
        "TaskAssignment",
        back_populates="completions",
        doc="Many-to-one relationship to task assignment"
    )