from typing import Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.task_status import TaskStatus
from app.models.daily_task_update import DailyTaskUpdate

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: str) -> Optional[Task]:
        return self.db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignments).joinedload(TaskAssignment.assignee),
            joinedload(Task.daily_updates).joinedload(DailyTaskUpdate.status)
        ).filter(Task.id == task_id).first()

    def list_tasks(
        self,
        assigned_user_id: Optional[str] = None,
        created_by_user_id: Optional[str] = None,
        manager_employee_ids: Optional[list[str]] = None,
        priority: Optional[str] = None,
        is_overdue: Optional[bool] = None,
        due_date: Optional[date] = None
    ) -> list[Task]:
        query = self.db.query(Task).options(
            joinedload(Task.creator),
            joinedload(Task.assignments).joinedload(TaskAssignment.assignee),
            joinedload(Task.daily_updates).joinedload(DailyTaskUpdate.status)
        )

        if assigned_user_id:
            query = query.join(Task.assignments).filter(
                TaskAssignment.user_id == assigned_user_id,
                TaskAssignment.is_active == True
            )
        elif manager_employee_ids is not None:
            # Filter tasks assigned to or created by team
            query = query.join(Task.assignments).filter(
                TaskAssignment.user_id.in_(manager_employee_ids),
                TaskAssignment.is_active == True
            )

        if created_by_user_id:
            query = query.filter(Task.created_by == created_by_user_id)

        if priority:
            query = query.filter(Task.priority == priority)

        if due_date:
            query = query.filter(Task.due_date == due_date)

        tasks = query.order_by(Task.due_date.asc()).all()

        if is_overdue is not None:
            today = date.today()
            if is_overdue:
                tasks = [t for t in tasks if t.due_date < today and not self._is_task_completed(t)]
            else:
                tasks = [t for t in tasks if t.due_date >= today or self._is_task_completed(t)]

        return tasks

    def _is_task_completed(self, task: Task) -> bool:
        if not task.daily_updates:
            return False
        latest = sorted(task.daily_updates, key=lambda u: (u.update_date, u.submitted_at), reverse=True)[0]
        return latest.status.name == "COMPLETED"

    def create_task(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_active_assignment(self, task_id: str) -> Optional[TaskAssignment]:
        return self.db.query(TaskAssignment).options(
            joinedload(TaskAssignment.assignee),
            joinedload(TaskAssignment.assigner)
        ).filter(
            TaskAssignment.task_id == task_id,
            TaskAssignment.is_active == True
        ).first()

    def assign_task(self, task_id: str, user_id: str, assigned_by: str) -> TaskAssignment:
        # Deactivate previous active assignments
        self.db.query(TaskAssignment).filter(
            TaskAssignment.task_id == task_id,
            TaskAssignment.is_active == True
        ).update({"is_active": False})

        new_assignment = TaskAssignment(
            task_id=task_id,
            user_id=user_id,
            assigned_by=assigned_by,
            is_active=True
        )
        self.db.add(new_assignment)
        self.db.commit()
        self.db.refresh(new_assignment)
        return new_assignment

    def list_statuses(self) -> list[TaskStatus]:
        return self.db.query(TaskStatus).filter(TaskStatus.is_active == True).order_by(TaskStatus.id.asc()).all()

    def get_status_by_id(self, status_id: int) -> Optional[TaskStatus]:
        return self.db.query(TaskStatus).filter(TaskStatus.id == status_id).first()

    def get_status_by_name(self, name: str) -> Optional[TaskStatus]:
        return self.db.query(TaskStatus).filter(TaskStatus.name == name).first()
