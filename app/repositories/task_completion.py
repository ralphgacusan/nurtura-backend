# repositories/task_completion.py

"""
Repository for managing TaskCompletion ORM objects.
Provides CRUD and query operations specifically for task completions.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.task_completion import TaskCompletion
from app.schemas.task_completion import TaskCompletionCreate, TaskCompletionUpdate


class TaskCompletionRepository:
    """
    Repository for interacting with TaskCompletion records in the database.

    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_completion(self, completion: TaskCompletionCreate) -> TaskCompletion:
        """
        Create a new task completion entry.
        """
        db_completion = TaskCompletion(
            task_assignment_id=completion.task_assignment_id,
            scheduled_date=completion.scheduled_date,
            status=completion.status,
            completed_at=completion.completed_at
        )
        self.db.add(db_completion)
        await self.db.flush()  # assign primary key
        return db_completion

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(self, completion_id: int, eager_load: bool = False) -> TaskCompletion | None:
        """
        Retrieve a task completion by its ID.

        Args:
            completion_id (int): Primary key.
            eager_load (bool): Whether to eagerly load related assignment.

        Returns:
            TaskCompletion | None
        """
        stmt = select(TaskCompletion).where(TaskCompletion.completion_id == completion_id)

        if eager_load:
            stmt = stmt.options(selectinload(TaskCompletion.assignment))

        result = await self.db.execute(stmt)
        return result.scalars().first()

    # ---------------------------
    # LIST / QUERY
    # ---------------------------
    async def list_by_assignment(self, task_assignment_id: int, eager_load: bool = False) -> list[TaskCompletion]:
        """
        List all completions for a specific task assignment.
        """
        stmt = select(TaskCompletion).where(TaskCompletion.task_assignment_id == task_assignment_id)

        if eager_load:
            stmt = stmt.options(selectinload(TaskCompletion.assignment))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_completion(self, completion_id: int, updates: TaskCompletionUpdate) -> TaskCompletion | None:
        """
        Update fields of a task completion entry.
        """
        completion = await self.get_by_id(completion_id, eager_load=True)
        if not completion:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(completion, field, value)

        self.db.add(completion)
        await self.db.commit()
        await self.db.refresh(completion)
        return completion

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_completion(self, completion_id: int) -> bool:
        """
        Delete a task completion by ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        completion = await self.get_by_id(completion_id, eager_load=True)
        if not completion:
            return False

        await self.db.delete(completion)
        await self.db.commit()
        return True