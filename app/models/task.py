"""
models/task.py

Defines the Task SQLAlchemy model and associated enums.
Tasks belong to a care space and are assigned by a user.
They contain scheduling information, priority, and description.

Fields:
- task_id: Primary key.
- title: Short task title.
- description: Optional detailed instructions.
- care_space_id: FK to care_spaces.
- assigned_by: FK to users (creator of task).
- due_date: Task due date/time.
- priority: Task priority enum.
- created_at: Timestamp of creation.
- updated_at: Timestamp of last update.

Relationships:
- care_space: Many-to-one with CareSpace.
- creator: Many-to-one with User.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone
import enum

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


# ---------------------------
# Task Enums
# ---------------------------
class TaskPriority(str, enum.Enum):
    """Priority level of the task."""
    low = "low"
    medium = "medium"
    high = "high"


# ---------------------------
# Task Model
# ---------------------------
class Task(Base):
    """
    SQLAlchemy model representing a task inside a care space.

    Attributes:
        task_id (int): Primary key.
        title (str): Short title of task.
        description (str | None): Optional detailed instructions.
        care_space_id (int): Linked care space.
        assigned_by (int): User who created the task.
        due_date (datetime): Due date/time of task.
        priority (TaskPriority | None): Optional priority level.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        care_space (CareSpace): Related care space.
        creator (User): User who assigned the task.
    """

    __tablename__ = "tasks"

    # ---------------------------
    # Columns
    # ---------------------------
    task_id = Column(Integer, primary_key=True, index=True, doc="Primary key for task")

    title = Column(
        String(100),
        nullable=False,
        doc="Short title of task"
    )

    description = Column(
        Text,
        nullable=True,
        doc="Optional detailed instructions"
    )

    care_space_id = Column(
        Integer,
        ForeignKey("care_spaces.care_space_id"),
        nullable=False,
        doc="FK to care_spaces"
    )

    assigned_by = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        doc="FK to users (creator)"
    )

    due_date = Column(
        DateTime(timezone=True),
        nullable=False,
        doc="Task due date/time"
    )

    priority = Column(
        Enum(TaskPriority),
        nullable=True,
        doc="Optional task priority"
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        doc="Creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        doc="Last update timestamp"
    )

    # ---------------------------
    # Relationships
    # ---------------------------

    care_space = relationship(
        "CareSpace",
        back_populates="tasks",
        doc="Many-to-one relationship to care space"
    )

    creator = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[assigned_by],
        doc="Many-to-one relationship to user who created the task"
    )

    assignments = relationship(
        "TaskAssignment",
        back_populates="task",
        cascade="all, delete-orphan",
        doc="One-to-many relationship to task assignments"
    )

    schedules = relationship(
        "Schedule",
        back_populates="task",
        cascade="all, delete-orphan",
        doc="One-to-many relationship to schedules"
    )