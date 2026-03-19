# app/services/dashboard.py

from datetime import datetime, timezone, timedelta
from app.repositories.dashboard import DashboardRepository
from app.repositories.task import TaskRepository
from app.repositories.task_assignment import TaskAssignmentRepository
from app.repositories.task_completion import TaskCompletionRepository
from app.services.care_space_member import CareSpaceMemberService
from app.models.user import User

class DashboardService:
    """
    Service for generating dynamic dashboard metrics
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        assignment_repo: TaskAssignmentRepository,
        completion_repo: TaskCompletionRepository,
        care_space_member_service: CareSpaceMemberService
    ):
        self.task_repo = task_repo
        self.assignment_repo = assignment_repo
        self.completion_repo = completion_repo
        self.care_space_member_service = care_space_member_service
        

    def _get_date_range(self, filter: str):
        now = datetime.now(timezone.utc)
        if filter == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif filter == "week":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif filter == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_month = (start.month % 12) + 1
            end_year = start.year + (start.month // 12)
            end = start.replace(month=end_month, year=end_year)
        else:
            start = end = None
        return start, end

    async def get_user_dashboard(self, current_user: User, filter: str = "today") -> dict:
        start, end = self._get_date_range(filter)
        member_id = current_user.user_id

        # 1️⃣ Get all assignments for the current user
        assignments = await self.assignment_repo.list_by_user(member_id, eager_load=True)

        total_tasks = 0
        completed = 0
        missed = 0
        pending = 0
        task_ids_seen = set()

        for assignment in assignments:
            task = await self.task_repo.get_by_id(assignment.task_id, eager_load=True)
            if not task:
                continue

            # Skip counting the same task multiple times
            if task.task_id in task_ids_seen:
                continue
            task_ids_seen.add(task.task_id)

            # Apply date filter via schedules
            schedules = getattr(task, "schedules", [])
            if start and end:
                if not any(s.start_time and start <= s.start_time < end for s in schedules):
                    continue

            total_tasks += 1

            # ✅ Fetch completions for this assignment only
            completions = await self.completion_repo.list_by_assignment(assignment.assignment_id)
            for c in completions:
                if c.status == "completed":
                    completed += 1
                elif c.status == "missed":
                    missed += 1
                elif c.status == "pending":
                    pending += 1

        success_rate = round((completed / total_tasks * 100), 2) if total_tasks else 0
        care_spaces_count = await self.care_space_member_service.count_user_care_spaces(member_id)

        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "missed": missed,
            "pending": pending,
            "success_rate": success_rate,
            "care_spaces_count": care_spaces_count
        }