"""
models/task_assignment.py

Defines the TaskAssignment SQLAlchemy model.
Task assignments link tasks to users who are assigned to do them.
They also store when the task was acknowledged.

Fields:
- assignment_id: Primary key.
- task_id: FK to tasks.
- assigned_to: FK to users.
- acknowledged_at: Optional timestamp when task was viewed.
- created_at: Timestamp of creation.
- updated_at: Timestamp of last update.

Relationships:
- task: Many-to-one with Task.
- user: Many-to-one with User.
"""

# ---------------------------
# Standard Library Imports
# ---------------------------
from datetime import datetime, timezone

# ---------------------------
# SQLAlchemy Imports
# ---------------------------
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


# ---------------------------
# TaskAssignment Model
# ---------------------------
class TaskAssignment(Base):
    """
    SQLAlchemy model representing assignment of a task to a user.

    Attributes:
        assignment_id (int): Primary key.
        task_id (int): Linked task.
        assigned_to (int): User assigned to task.
        acknowledged_at (datetime | None): When user viewed task.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        task (Task): Related task.
        user (User): Assigned user.
    """

    __tablename__ = "task_assignments"

    # ---------------------------
    # Columns
    # ---------------------------
    assignment_id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Primary key for assignment"
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.task_id"),
        nullable=False,
        doc="FK to tasks"
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        doc="FK to users"
    )

    acknowledged_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when task was first viewed"
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

    task = relationship(
        "Task",
        back_populates="assignments",
        doc="Many-to-one relationship to task"
    )

    user = relationship(
        "User",
        back_populates="task_assignments",
        foreign_keys=[assigned_to],
        doc="Many-to-one relationship to assigned user"
    )

    completions = relationship(
        "TaskCompletion",
        back_populates="assignment",
        cascade="all, delete-orphan",
        doc="One-to-many relationship to task completions"
    )