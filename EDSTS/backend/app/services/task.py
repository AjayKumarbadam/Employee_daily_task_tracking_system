from typing import Optional
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskAssignmentResponse, LatestUpdateBrief

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.user_repo = UserRepository(db)

    def get_task_by_id(self, task_id: str) -> TaskResponse:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return self._to_response(task)

    def list_tasks(
        self,
        current_user: User,
        user_roles: list[str],
        assigned_user_id: Optional[str] = None,
        priority: Optional[str] = None,
        is_overdue: Optional[bool] = None,
        due_date: Optional[date] = None
    ) -> list[TaskResponse]:
        # Ownership / Scope Check
        manager_employee_ids = None
        filter_assigned_id = assigned_user_id

        if "ADMIN" in user_roles:
            # Admin can view all or filter by any assigned user
            pass
        elif "MANAGER" in user_roles:
            # Manager can view their own tasks, tasks created by them, or tasks of their direct subordinates
            subordinates = self.user_repo.list_all(manager_id=current_user.id)
            sub_ids = [s.id for s in subordinates]
            sub_ids.append(current_user.id)
            if filter_assigned_id:
                if filter_assigned_id not in sub_ids:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access tasks outside your team")
            else:
                manager_employee_ids = sub_ids
        else:
            # Employee can ONLY view tasks assigned to themselves
            filter_assigned_id = current_user.id

        tasks = self.task_repo.list_tasks(
            assigned_user_id=filter_assigned_id,
            manager_employee_ids=manager_employee_ids,
            priority=priority,
            is_overdue=is_overdue,
            due_date=due_date
        )
        return [self._to_response(t) for t in tasks]

    def create_task(self, task_data: TaskCreate, creator_id: str) -> TaskResponse:
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority.value if hasattr(task_data.priority, "value") else task_data.priority,
            due_date=task_data.due_date,
            created_by=creator_id
        )
        created = self.task_repo.create_task(new_task)

        if task_data.assigned_to_user_id:
            assignee = self.user_repo.get_by_id(task_data.assigned_to_user_id)
            if not assignee:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignee user not found")
            self.task_repo.assign_task(
                task_id=created.id,
                user_id=task_data.assigned_to_user_id,
                assigned_by=creator_id
            )

        return self.get_task_by_id(created.id)

    def update_task(self, task_id: str, task_data: TaskUpdate, current_user: User, user_roles: list[str]) -> TaskResponse:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        # Check permissions: Admin or Manager who created it or manages the assignee
        if "ADMIN" not in user_roles and task.created_by != current_user.id:
            active_assign = self.task_repo.get_active_assignment(task_id)
            if not active_assign or active_assign.assignee.manager_id != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this task")

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.priority is not None:
            task.priority = task_data.priority.value if hasattr(task_data.priority, "value") else task_data.priority
        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        self.task_repo.update_task(task)
        return self.get_task_by_id(task.id)

    def assign_task(self, task_id: str, target_user_id: str, assigner: User, user_roles: list[str]) -> TaskResponse:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")
        if not target_user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign task to deactivated user")

        if "ADMIN" not in user_roles:
            if target_user.manager_id != assigner.id and target_user.id != assigner.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only assign tasks to employees reporting to you")

        self.task_repo.assign_task(
            task_id=task_id,
            user_id=target_user_id,
            assigned_by=assigner.id
        )
        return self.get_task_by_id(task.id)

    def _to_response(self, task: Task) -> TaskResponse:
        # Determine latest update & status
        latest_update = None
        is_completed = False
        if task.daily_updates:
            sorted_updates = sorted(task.daily_updates, key=lambda u: (u.update_date, u.submitted_at), reverse=True)
            top = sorted_updates[0]
            latest_update = LatestUpdateBrief(
                id=top.id,
                status_id=top.status_id,
                status_name=top.status.name if top.status else "UNKNOWN",
                progress_percentage=top.progress_percentage,
                remarks=top.remarks,
                update_date=top.update_date,
                submitted_at=top.submitted_at
            )
            if top.status and top.status.name == "COMPLETED":
                is_completed = True

        today = date.today()
        is_overdue = (task.due_date < today) and (not is_completed)

        # Active assignment
        current_assignment = None
        if task.assignments:
            active = next((a for a in task.assignments if a.is_active), None)
            if active and active.assignee:
                current_assignment = TaskAssignmentResponse(
                    id=active.id,
                    task_id=active.task_id,
                    user_id=active.user_id,
                    assignee={
                        "id": active.assignee.id,
                        "employee_id": active.assignee.employee_id,
                        "name": active.assignee.name,
                        "email": active.assignee.email,
                        "department": active.assignee.department
                    },
                    assigned_by=active.assigned_by,
                    assigned_at=active.assigned_at,
                    is_active=active.is_active
                )

        creator_brief = None
        if task.creator:
            creator_brief = {
                "id": task.creator.id,
                "employee_id": task.creator.employee_id,
                "name": task.creator.name,
                "email": task.creator.email,
                "department": task.creator.department
            }

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            due_date=task.due_date,
            created_by=task.created_by,
            creator=creator_brief,
            created_at=task.created_at,
            updated_at=task.updated_at,
            is_overdue=is_overdue,
            current_assignment=current_assignment,
            latest_update=latest_update
        )
