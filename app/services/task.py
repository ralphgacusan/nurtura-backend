"""
services/task_service.py

Service layer for managing Task operations.

Responsibilities:
- Create, read, update, delete tasks
- Manage related assignments, schedules, and completions
"""



# ---------------------------
# Local App Imports
# ---------------------------
from app.repositories.task import TaskRepository
from app.repositories.task_assignment import TaskAssignmentRepository
from app.repositories.schedule import ScheduleRepository
from app.repositories.task_completion import TaskCompletionRepository
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskRead, 
    TaskReadExtended, TaskAssignmentRead, 
    TaskScheduleRead, TaskDateFilter, TaskPriority, 
    TaskStatus
)
from app.schemas.task_assignment import TaskAssignmentCreate
from app.schemas.schedule import ScheduleCreate
from app.schemas.task_completion import TaskCompletionCreate
from app.models.user import User
from app.models.task import Task
from app.models.care_space_member import CareSpaceMember
from datetime import datetime, timezone, timedelta

from app.models.care_space_member import CareSpaceMember
from app.core.exceptions import (
    task_creation_failed_exception,
    task_assignment_creation_failed_exception,
    task_schedule_creation_failed_exception,
    task_completion_creation_failed_exception,
    task_completion_not_found_exception,
    task_assignment_not_found_exception,
    invalid_input_exception,
    task_update_failed_exception
)
from app.core.permissions import ensure_member_and_can_manage_tasks, ensure_member
from app.services.care_space_member import CareSpaceMemberService
from app.schemas.task_completion import CompletionStatus, TaskStatusUpdateRequest, TaskCompletionRead

# ---------------------------
# Task Service
# ---------------------------
class TaskService:
    """
    Service for managing Task operations.

    Handles creation, updates, deletion, and linking assignments, schedules, and completions.
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        assignment_repo: TaskAssignmentRepository,
        schedule_repo: ScheduleRepository,
        completion_repo: TaskCompletionRepository,
        care_space_member_service: CareSpaceMemberService,
    ):
        self.task_repo = task_repo
        self.assignment_repo = assignment_repo
        self.schedule_repo = schedule_repo
        self.completion_repo = completion_repo
        self.care_space_member_service = care_space_member_service

    
    def _apply_filters(
        self,
        tasks,
        date_filter: TaskDateFilter,
        priority: TaskPriority | None,
        status: TaskStatus | None
    ):
        now = datetime.now(timezone.utc)

        # ---------------------------
        # DATE RANGE
        # ---------------------------
        if date_filter == TaskDateFilter.today:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)

        elif date_filter == TaskDateFilter.week:
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)

        elif date_filter == TaskDateFilter.month:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = (start.replace(month=start.month % 12 + 1, year=start.year + (start.month // 12)))

        else:
            start = end = None

        filtered = []

        for task in tasks:

            # ---------------------------
            # PRIORITY FILTER
            # ---------------------------
            if priority and task.priority != priority:
                continue

            # ---------------------------
            # DATE FILTER (via schedules)
            # ---------------------------
            if start and end:
                schedules = getattr(task, "schedules", [])

                if not any(
                    sched.start_time and start <= sched.start_time < end
                    for sched in schedules
                ):
                    continue

            # ---------------------------
            # STATUS FILTER (via completions)
            # ---------------------------
            if status:
                completions = getattr(task, "completions", [])

                if not any(c.status == status for c in completions):
                    continue

            filtered.append(task)

        return filtered

    # ---------------------------
    # CREATE TASK
    # ---------------------------
    async def create_task(
        self,
        care_space_id: int,
        task_data: TaskCreate,
        assigned_user_ids: list[int] = None,
        schedule_data: list[ScheduleCreate] = None,
        member: CareSpaceMember = None
    ) -> TaskRead:
        # Permission check
        ensure_member_and_can_manage_tasks(member)

        task = Task(
            title=task_data.title,
            description=task_data.description,
            care_space_id=care_space_id,
            assigned_by=member.user_id,
            due_date=task_data.due_date,
            priority=task_data.priority
        )

        try:
            task = await self.task_repo.create_task(task)
            await self.task_repo.db.commit()
        except Exception:
            raise task_creation_failed_exception

        # Create assignments
        assignments = []
        if assigned_user_ids:
            for user_id in assigned_user_ids:
                await self.care_space_member_service.ensure_user_is_member(
                    task.care_space_id, user_id
                )
                try:
                    assignment = await self.assignment_repo.create_assignment(
                        TaskAssignmentCreate(task_id=task.task_id, assigned_to=user_id)
                    )
                    assignments.append(assignment)
                except Exception:
                    raise task_assignment_creation_failed_exception
            await self.assignment_repo.db.commit()

        # Create schedules
        schedules = []
        if schedule_data:
            for sched in schedule_data:
                try:
                    sched_with_id = sched.model_copy(update={"task_id": task.task_id})
                    schedule = await self.schedule_repo.create_schedule(sched_with_id)
                    schedules.append(schedule)
                except Exception:
                    raise task_schedule_creation_failed_exception
            await self.schedule_repo.db.commit()

        # Create completions
        for assignment in assignments:
            for sched in schedules:
                try:
                    await self.completion_repo.create_completion(
                        TaskCompletionCreate(
                            task_assignment_id=assignment.assignment_id,
                            scheduled_date=sched.start_time.date(),
                            status="pending"
                        )
                    )
                except Exception:
                    raise task_completion_creation_failed_exception
        await self.completion_repo.db.commit()

        # Reload task fully
        task = await self.task_repo.get_by_id(task.task_id, eager_load=True)
        return TaskRead.model_validate(task)

    # ---------------------------
    # HELPER: populate completions
    # ---------------------------
    async def _populate_completions(self, task_read: TaskReadExtended) -> TaskReadExtended:
        """Fetch completions for all assignments and attach to task_read"""
        task_read.completions = []
        for assignment in getattr(task_read, "assignments", []):
            completions = await self.completion_repo.list_by_assignment(assignment.assignment_id)
            task_read.completions.extend([TaskCompletionRead.model_validate(c) for c in completions])
        return task_read

    # ---------------------------
    # LIST TASKS BY CARE SPACE
    # ---------------------------
    async def list_tasks_by_care_space(
        self,
        care_space_id: int,
        member: CareSpaceMember = None,
        eager_load: bool = True
    ) -> list[TaskReadExtended]:
        if member:
            ensure_member_and_can_manage_tasks(member)

        tasks = await self.task_repo.list_by_care_space(care_space_id, eager_load=eager_load)
        task_list = []

        for task in tasks:
            task_read = TaskReadExtended.model_validate(task)
            task_read.assignments = [
                TaskAssignmentRead.model_validate(a) for a in getattr(task, "assignments", [])
            ]
            task_read.schedules = [
                TaskScheduleRead.model_validate(s) for s in getattr(task, "schedules", [])
            ]
            task_read = await self._populate_completions(task_read)
            task_list.append(task_read)

        return task_list

    # ---------------------------
    # GET TASK BY ID
    # ---------------------------
    async def get_task_full_by_id(
        self,
        task_id: int,
        member: CareSpaceMember = None
    ) -> TaskReadExtended:
        if member:
            ensure_member(member)

        task = await self.task_repo.get_by_id(task_id, eager_load=True)
        if not task:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Task not found")

        task_read = TaskReadExtended.model_validate(task)
        task_read.assignments = [
            TaskAssignmentRead.model_validate(a) for a in getattr(task, "assignments", [])
        ]
        task_read.schedules = [
            TaskScheduleRead.model_validate(s) for s in getattr(task, "schedules", [])
        ]
        task_read = await self._populate_completions(task_read)
        return task_read

    # ---------------------------
    # LIST TASKS BY MEMBER
    # ---------------------------
    async def list_tasks_by_member(
        self,
        member_id: int,
        eager_load: bool = True
    ) -> list[TaskReadExtended]:
        assignments = await self.assignment_repo.list_by_user(member_id, eager_load=eager_load)
        task_ids = list({assignment.task_id for assignment in assignments})
        tasks = []

        for task_id in task_ids:
            task = await self.task_repo.get_by_id(task_id, eager_load=eager_load)
            if task:
                task_read = TaskReadExtended.model_validate(task)
                task_read.assignments = [
                    TaskAssignmentRead.model_validate(a) for a in getattr(task, "assignments", [])
                ]
                task_read.schedules = [
                    TaskScheduleRead.model_validate(s) for s in getattr(task, "schedules", [])
                ]
                task_read = await self._populate_completions(task_read)
                tasks.append(task_read)

        return tasks

    # ---------------------------
    # LIST TASKS FOR CURRENT USER
    # ---------------------------
    async def list_tasks_for_current_user(
        self,
        current_user: User,
        eager_load: bool = True,
        date_filter: TaskDateFilter = TaskDateFilter.all,
        priority: TaskPriority | None = None,
        status: TaskStatus | None = None
    ) -> list[TaskReadExtended]:
        member_id = current_user.user_id
        assignments = await self.assignment_repo.list_by_user(member_id, eager_load=eager_load)
        task_ids = list({assignment.task_id for assignment in assignments})
        tasks = []

        for task_id in task_ids:
            task = await self.task_repo.get_by_id(task_id, eager_load=eager_load)
            if task:
                task_read = TaskReadExtended.model_validate(task)
                task_read.assignments = [
                    TaskAssignmentRead.model_validate(a) for a in getattr(task, "assignments", [])
                ]
                task_read.schedules = [
                    TaskScheduleRead.model_validate(s) for s in getattr(task, "schedules", [])
                ]
                task_read = await self._populate_completions(task_read)
                tasks.append(task_read)

        tasks = self._apply_filters(tasks, date_filter, priority, status)

        return tasks
    

   
    
    # ---------------------------
    # LIST TASKS CREATED BY CURRENT USER
    # ---------------------------
    async def list_tasks_created_by_current_user(
        self,
        current_user: User,
        eager_load: bool = True,
        date_filter: TaskDateFilter = TaskDateFilter.all,
        priority: TaskPriority | None = None,
        status: TaskStatus | None = None
    ) -> list[TaskReadExtended]:

        member_id = current_user.user_id

        tasks = await self.task_repo.list_task_by_creator(
            member_id,
            eager_load=eager_load
        )

        result = []

        for task in tasks:
            if task:
                task_read = TaskReadExtended.model_validate(task)

                task_read.assignments = [
                    TaskAssignmentRead.model_validate(a)
                    for a in getattr(task, "assignments", [])
                ]

                task_read.schedules = [
                    TaskScheduleRead.model_validate(s)
                    for s in getattr(task, "schedules", [])
                ]

                task_read = await self._populate_completions(task_read)

                result.append(task_read)
        
        result = self._apply_filters(
            result,
            date_filter,
            priority,
            status
        )

        return result
    
   # ---------------------------
    # UPDATE TASK
    # ---------------------------
    async def update_task(
        self,
        task_id: int,
        updates: TaskUpdate,
        assigned_user_ids: list[int] | None = None,
        schedule_data: list[ScheduleCreate] | None = None,
        member: CareSpaceMember | None = None
    ) -> TaskReadExtended:

        # permission only if changing assignments or schedules
        if member and (
            assigned_user_ids is not None
            or schedule_data is not None
        ):
            ensure_member_and_can_manage_tasks(member)

        # -----------------
        # UPDATE TASK FIELDS
        # -----------------
        task = await self.task_repo.update_task(task_id, updates)

        if not task:
            from fastapi import HTTPException
            raise HTTPException(404, "Task not found")

        # -----------------
        # UPDATE ASSIGNMENTS
        # -----------------

        existing_assignments = await self.assignment_repo.list_by_task(task_id)
        existing_user_ids = {a.assigned_to for a in existing_assignments}

        # ADD assignments
        if assigned_user_ids is not None:

            for user_id in assigned_user_ids:

                if user_id not in existing_user_ids:

                    await self.care_space_member_service.ensure_user_is_member(
                        task.care_space_id,
                        user_id
                    )

                    new_assignment = await self.assignment_repo.create_assignment(
                        TaskAssignmentCreate(
                            task_id=task_id,
                            assigned_to=user_id
                        )
                    )

                    schedules = await self.schedule_repo.list_by_task(task_id)

                    for sched in schedules:
                        await self.completion_repo.create_completion(
                            TaskCompletionCreate(
                                task_assignment_id=new_assignment.assignment_id,
                                scheduled_date=sched.start_time.date(),
                                status="pending"
                            )
                        )

            # REMOVE assignments
            for assignment in existing_assignments:

                if assignment.assigned_to not in assigned_user_ids:

                    completions = await self.completion_repo.list_by_assignment(
                        assignment.assignment_id
                    )

                    for c in completions:
                        await self.completion_repo.delete_completion(
                            c.completion_id
                        )

                    await self.assignment_repo.delete_assignment(
                        assignment.assignment_id
                    )

            await self.assignment_repo.db.commit()
            await self.completion_repo.db.commit()

        # -----------------
        # UPDATE SCHEDULES
        # -----------------

        if schedule_data is not None:

            existing_schedules = await self.schedule_repo.list_by_task(task_id)
            assignments = await self.assignment_repo.list_by_task(task_id)

            # delete old schedules + completions
            for sched in existing_schedules:

                for assignment in assignments:

                    completions = await self.completion_repo.list_by_assignment(
                        assignment.assignment_id
                    )

                    for c in completions:
                        if c.scheduled_date == sched.start_time.date():
                            await self.completion_repo.delete_completion(
                                c.completion_id
                            )

                await self.schedule_repo.delete_schedule(
                    sched.schedule_id
                )

            await self.schedule_repo.db.commit()
            await self.completion_repo.db.commit()

            # create new schedules

            new_schedules = []

            for sched in schedule_data:

                sched_with_task = sched.model_copy(
                    update={"task_id": task_id}
                )

                new_sched = await self.schedule_repo.create_schedule(
                    sched_with_task
                )

                new_schedules.append(new_sched)

            await self.schedule_repo.db.commit()

            # recreate completions

            assignments = await self.assignment_repo.list_by_task(task_id)

            for assignment in assignments:

                for sched in new_schedules:

                    await self.completion_repo.create_completion(
                        TaskCompletionCreate(
                            task_assignment_id=assignment.assignment_id,
                            scheduled_date=sched.start_time.date(),
                            status="pending"
                        )
                    )

            await self.completion_repo.db.commit()

        # -----------------
        # RELOAD FULL TASK
        # -----------------

        task = await self.task_repo.get_by_id(
            task_id,
            eager_load=True
        )

        if not task:
            raise Exception("Task missing after update")

        task_read = TaskReadExtended.model_validate(task)

        task_read.assignments = [
            TaskAssignmentRead.model_validate(a)
            for a in getattr(task, "assignments", [])
        ]

        task_read.schedules = [
            TaskScheduleRead.model_validate(s)
            for s in getattr(task, "schedules", [])
        ]

        return task_read
    

    # ---------------------------
    #   DELETE TASK
    # ---------------------------
    async def delete_task(
        self,
        task_id: int,
        member: CareSpaceMember | None = None
    ) -> bool:
        """
        Delete a task and all related assignments, completions, and schedules.

        Args:
            task_id (int): Task to delete
            member (CareSpaceMember | None): Optional permission check

        Returns:
            bool: True if deleted, False if task not found
        """
        # Optional permission check
        if member:
            ensure_member_and_can_manage_tasks(member)

        # Load task with eager relations
        task = await self.task_repo.get_by_id(task_id, eager_load=True)
        if not task:
            return False  # task not found

        # Delete all completions
        for assignment in getattr(task, "assignments", []):
            completions = await self.completion_repo.list_by_assignment(assignment.assignment_id)
            for completion in completions:
                await self.completion_repo.delete_completion(completion.completion_id)

        # Delete all assignments
        for assignment in getattr(task, "assignments", []):
            await self.assignment_repo.delete_assignment(assignment.assignment_id)

        # Delete all schedules
        for schedule in getattr(task, "schedules", []):
            await self.schedule_repo.delete_schedule(schedule.schedule_id)

        # Commit deletions of related objects
        await self.completion_repo.db.commit()
        await self.assignment_repo.db.commit()
        await self.schedule_repo.db.commit()

        # Finally, delete the task itself
        deleted = await self.task_repo.delete_task(task_id)
        return deleted
    

    # ---------------------------
    # UPDATE TASK STATUS / ACKNOWLEDGE
    # ---------------------------
    async def update_task_status(
        self,
        data: TaskStatusUpdateRequest
    ) -> dict:
        """
        Dynamically update:
        - Task completion status (completed, missed, pending)
        - Assignment acknowledgment (seen)
        
        Uses predefined exceptions from core/exceptions.py
        """
        result = {}

        try:
            # ---------------------------
            # 1️⃣ Acknowledge assignment
            # ---------------------------
            if data.acknowledge and data.assignment_id:
                assignment = await self.assignment_repo.get_by_id(data.assignment_id)
                if not assignment:
                    raise task_assignment_not_found_exception

                assignment.acknowledged_at = datetime.now(timezone.utc)
                self.assignment_repo.db.add(assignment)
                await self.assignment_repo.db.commit()
                result["acknowledged_at"] = assignment.acknowledged_at

            # ---------------------------
            # 2️⃣ Update completion status
            # ---------------------------
            if data.completion_id and data.status:
                if data.status not in CompletionStatus.__members__:
                    raise invalid_input_exception

                from app.schemas.task_completion import TaskCompletionUpdate
                updates = TaskCompletionUpdate(
                    status=data.status,
                    completed_at=datetime.now(timezone.utc) if data.status == CompletionStatus.completed else None
                )

                updated_completion = await self.completion_repo.update_completion(data.completion_id, updates)
                if not updated_completion:
                    raise task_completion_not_found_exception

                result["completion"] = {
                    "completion_id": updated_completion.completion_id,
                    "status": updated_completion.status,
                    "completed_at": updated_completion.completed_at
                }

            if not result:
                # Nothing to update
                raise invalid_input_exception

        except (
            task_assignment_not_found_exception,
            task_completion_not_found_exception,
            invalid_input_exception
        ):
            # re-raise known exceptions
            raise
        except Exception as e:
            # fallback for unexpected errors
            raise task_update_failed_exception

        return result