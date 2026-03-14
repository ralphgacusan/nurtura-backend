# repositories/schedule.py

"""
Repository for managing Schedule ORM objects.
Provides CRUD and query operations specifically for task schedules.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


class ScheduleRepository:
    """
    Repository for interacting with Schedule records in the database.

    Args:
        db (AsyncSession): SQLAlchemy asynchronous session.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------------------------
    # CREATE
    # ---------------------------
    async def create_schedule(self, schedule: ScheduleCreate) -> Schedule:
        """
        Create a new schedule for a task.
        """
        db_schedule = Schedule(
            task_id=schedule.task_id,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            recurrence_type=schedule.recurrence_type,
            recurrence_days=schedule.recurrence_days
        )
        self.db.add(db_schedule)
        await self.db.flush()  # assign primary key
        return db_schedule

    # ---------------------------
    # READ
    # ---------------------------
    async def get_by_id(self, schedule_id: int, eager_load: bool = False) -> Schedule | None:
        """
        Retrieve a schedule by its ID.

        Args:
            schedule_id (int): Primary key.
            eager_load (bool): Whether to eagerly load related task.

        Returns:
            Schedule | None
        """
        stmt = select(Schedule).where(Schedule.schedule_id == schedule_id)

        if eager_load:
            stmt = stmt.options(selectinload(Schedule.task))

        result = await self.db.execute(stmt)
        return result.scalars().first()

    # ---------------------------
    # LIST / QUERY
    # ---------------------------
    async def list_by_task(self, task_id: int, eager_load: bool = False) -> list[Schedule]:
        """
        List all schedules for a specific task.
        """
        stmt = select(Schedule).where(Schedule.task_id == task_id)

        if eager_load:
            stmt = stmt.options(selectinload(Schedule.task))

        result = await self.db.execute(stmt)
        return result.scalars().all()

    # ---------------------------
    # UPDATE
    # ---------------------------
    async def update_schedule(self, schedule_id: int, updates: ScheduleUpdate) -> Schedule | None:
        """
        Update fields of a schedule.
        """
        schedule = await self.get_by_id(schedule_id, eager_load=True)
        if not schedule:
            return None

        for field, value in updates.model_dump(exclude_unset=True).items():
            setattr(schedule, field, value)

        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    # ---------------------------
    # DELETE
    # ---------------------------
    async def delete_schedule(self, schedule_id: int) -> bool:
        """
        Delete a schedule by ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        schedule = await self.get_by_id(schedule_id, eager_load=True)
        if not schedule:
            return False

        await self.db.delete(schedule)
        await self.db.commit()
        return True