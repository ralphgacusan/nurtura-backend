# repositories/task_assignment.py

"""
Repository for managing TaskAssignment ORM objects.
Provides CRUD and query operations specifically for task assignments.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.task_assignment import TaskAssignment
from app.schemas.task_assignment import TaskAssignmentCreate, TaskAssignmentUpdate


class TaskAssignmentRepository:
    """
    Repository for interacting with TaskAssignment records in the database.

    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_assignment(self, assignment: TaskAssignmentCreate) -> TaskAssignment:
        """
        Create a new task assignment.
        """
        db_assignment = TaskAssignment(
            task_id=assignment.task_id,
            assigned_to=assignment.assigned_to,
            acknowledged_at=assignment.acknowledged_at
        )
        self.db.add(db_assignment)
        await self.db.flush()  # assign primary key
        return db_assignment

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(self, assignment_id: int, eager_load: bool = False) -> TaskAssignment | None:
        """
        Retrieve a task assignment by its ID.

        Args:
            assignment_id (int): Primary key.
            eager_load (bool): Whether to eagerly load related task and user.

        Returns:
            TaskAssignment | None
        """
        stmt = select(TaskAssignment).where(TaskAssignment.assignment_id == assignment_id)

        if eager_load:
            stmt = stmt.options(
                selectinload(TaskAssignment.task),
                selectinload(TaskAssignment.user),
                selectinload(TaskAssignment.completions)
            )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    # ---------------------------
    # LIST / QUERY
    # ---------------------------
    async def list_by_task(self, task_id: int, eager_load: bool = False) -> list[TaskAssignment]:
        """
        List all assignments for a specific task.
        """
        stmt = select(TaskAssignment).where(TaskAssignment.task_id == task_id)

        if eager_load:
            stmt = stmt.options(
                selectinload(TaskAssignment.user),
                selectinload(TaskAssignment.completions)
            )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_by_user(self, user_id: int, eager_load: bool = False) -> list[TaskAssignment]:
        """
        List all assignments assigned to a specific user.
        """
        stmt = select(TaskAssignment).where(TaskAssignment.assigned_to == user_id)

        if eager_load:
            stmt = stmt.options(
                selectinload(TaskAssignment.task),
                selectinload(TaskAssignment.completions)
            )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_assignment(self, assignment_id: int, updates: TaskAssignmentUpdate) -> TaskAssignment | None:
        """
        Update fields of a task assignment.
        """
        assignment = await self.get_by_id(assignment_id, eager_load=True)
        if not assignment:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(assignment, field, value)

        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_assignment(self, assignment_id: int) -> bool:
        """
        Delete a task assignment by ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        assignment = await self.get_by_id(assignment_id, eager_load=True)
        if not assignment:
            return False

        await self.db.delete(assignment)
        await self.db.commit()
        return True