# repositories/task.py

"""
Repository for managing Task ORM objects.
Provides CRUD and query operations specifically for tasks.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    """
    Repository for interacting with Task records in the database.
    
    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db  # store async session for DB operations

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_task(self, task: TaskCreate) -> Task:
        """
        Create a new task in the database.
        """
        db_task = Task(
            title=task.title,
            description=task.description,
            care_space_id=task.care_space_id,
            assigned_by=task.assigned_by,
            due_date=task.due_date,
            priority=task.priority
        )
        self.db.add(db_task)
        await self.db.flush()  # assign primary key
        return db_task

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(self, task_id: int, eager_load: bool = False) -> Task | None:
        """
        Retrieve a task by its ID.

        Args:
            task_id (int): Task primary key.
            eager_load (bool): Whether to eagerly load relationships (assignments, schedules).

        Returns:
            Task | None: Task object if found, else None.
        """
        stmt = select(Task).where(Task.task_id == task_id)

        if eager_load:
            stmt = stmt.options(
                selectinload(Task.assignments),  # eager load task assignments
                selectinload(Task.schedules)     # eager load task schedules
            )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    # ---------------------------
    # LIST / QUERY
    # ---------------------------
    async def list_by_care_space(self, care_space_id: int, eager_load: bool = False) -> list[Task]:
        """
        List all tasks under a specific care space.
        """
        stmt = select(Task).where(Task.care_space_id == care_space_id)

        if eager_load:
            stmt = stmt.options(
                selectinload(Task.assignments),
                selectinload(Task.schedules)
            )

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_task(self, task_id: int, updates: TaskUpdate) -> Task | None:
        """
        Update fields of a task using a Pydantic update schema.
        """
        task = await self.get_by_id(task_id, eager_load=True)
        if not task:
            return None  # task not found

        # apply only fields that were set in the update schema
        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(task, field, value)

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_task(self, task_id: int) -> bool:
        """
        Delete a task (hard delete) by ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        task = await self.get_by_id(task_id, eager_load=True)
        if not task:
            return False

        await self.db.delete(task)
        await self.db.commit()
        return True
    
    async def list_task_by_creator(self, current_user_id: int, eager_load: bool = False) -> list[Task]:
        """
        List all tasks under a specific creator.
        """
        stmt = select(Task).where(Task.assigned_by == current_user_id)

        if eager_load:
            stmt = stmt.options(
                selectinload(Task.assignments),
                selectinload(Task.schedules)
            )

        result = await self.db.execute(stmt)
        return result.scalars().all()
