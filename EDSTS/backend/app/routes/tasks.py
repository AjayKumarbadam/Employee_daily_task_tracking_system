from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.task import TaskService
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusResponse, TaskAssignRequest
from app.dependencies import get_current_user, get_current_user_roles, require_any_role
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/statuses", response_model=list[TaskStatusResponse])
def get_task_statuses(db: Session = Depends(get_db)):
    task_service = TaskService(db)
    return task_service.task_repo.list_statuses()

@router.get("", response_model=list[TaskResponse])
def get_tasks(
    assigned_user_id: Optional[str] = None,
    priority: Optional[str] = None,
    is_overdue: Optional[bool] = None,
    due_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.list_tasks(
        current_user=current_user,
        user_roles=roles,
        assigned_user_id=assigned_user_id,
        priority=priority,
        is_overdue=is_overdue,
        due_date=due_date
    )

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(require_any_role(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.create_task(task_data, creator_id=current_user.id)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.get_task_by_id(task_id)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(require_any_role(["ADMIN", "MANAGER"])),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.update_task(task_id, task_data, current_user, roles)

@router.post("/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    task_id: str,
    assign_req: TaskAssignRequest,
    current_user: User = Depends(require_any_role(["ADMIN", "MANAGER"])),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.assign_task(task_id, assign_req.user_id, current_user, roles)
