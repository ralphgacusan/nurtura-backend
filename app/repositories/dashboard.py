# app/repositories/dashboard.py

from sqlalchemy import select, func
from app.models.task import Task
from app.models.task_completion import TaskCompletion
from app.models.care_space_member import CareSpaceMember

class DashboardRepository:
    """
    Repository for fetching dashboard metrics.
    """

    def __init__(self, db):
        self.db = db

    # Total tasks for a user or care space
    async def count_tasks(self, user_id: int = None, care_space_id: int = None, start=None, end=None) -> int:
        query = select(func.count(Task.task_id))
        
        if user_id:
            query = query.join(TaskCompletion, Task.task_id == TaskCompletion.task_assignment_id)
        
        if care_space_id:
            query = query.where(Task.care_space_id == care_space_id)
        
        if start and end:
            query = query.where(Task.due_date >= start).where(Task.due_date < end)

        result = await self.db.execute(query)
        return result.scalar() or 0

    # Completed tasks
    async def count_completed_tasks(self, user_id: int = None, care_space_id: int = None, start=None, end=None) -> int:
        query = select(func.count(TaskCompletion.completion_id)).where(TaskCompletion.status == "completed")
        
        if user_id:
            query = query.where(TaskCompletion.user_id == user_id)
        
        if care_space_id:
            query = query.join(Task, Task.task_id == TaskCompletion.task_assignment_id).where(Task.care_space_id == care_space_id)
        
        if start and end:
            query = query.where(TaskCompletion.scheduled_date >= start).where(TaskCompletion.scheduled_date < end)

        result = await self.db.execute(query)
        return result.scalar() or 0

    # Missed tasks
    async def count_missed_tasks(self, user_id: int = None, start=None, end=None) -> int:
        query = select(func.count(TaskCompletion.completion_id)).where(TaskCompletion.status == "missed")
        if user_id:
            query = query.where(TaskCompletion.user_id == user_id)
        if start and end:
            query = query.where(TaskCompletion.scheduled_date >= start).where(TaskCompletion.scheduled_date < end)

        result = await self.db.execute(query)
        return result.scalar() or 0

    # Number of care spaces for a user
    async def count_care_spaces(self, user_id: int) -> int:
        query = select(func.count(CareSpaceMember.care_space_id)).where(CareSpaceMember.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0