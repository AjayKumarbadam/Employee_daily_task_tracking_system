from typing import Optional
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.daily_update import DailyUpdateRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.models.daily_task_update import DailyTaskUpdate
from app.models.user import User
from app.schemas.daily_update import DailyUpdateCreate, DailyUpdateUpdate, DailyUpdateResponse

class DailyUpdateService:
    def __init__(self, db: Session):
        self.db = db
        self.update_repo = DailyUpdateRepository(db)
        self.task_repo = TaskRepository(db)
        self.user_repo = UserRepository(db)

    def submit_daily_update(self, payload: DailyUpdateCreate, current_user: User, user_roles: list[str]) -> DailyUpdateResponse:
        task = self.task_repo.get_by_id(payload.task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        # Check ownership: User must be currently assigned to this task (or Admin)
        active_assignment = self.task_repo.get_active_assignment(payload.task_id)
        if not active_assignment or (active_assignment.user_id != current_user.id and "ADMIN" not in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only submit daily updates for tasks currently assigned to you."
            )

        status_obj = self.task_repo.get_status_by_id(payload.status_id)
        if not status_obj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status ID")

        # Business Rule Validations
        if status_obj.name == "COMPLETED" and payload.progress_percentage != 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completed task status requires 100% progress."
            )
        if status_obj.name == "NOT_STARTED" and payload.progress_percentage != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not Started task status must have 0% progress."
            )

        today = date.today()
        # Check if update exists for this task, user, and date
        target_date = payload.update_date or today
        existing = self.update_repo.get_by_task_user_date(payload.task_id, current_user.id, target_date)

        if existing:
            # Rule: Only today's update can be edited by employee
            if target_date < today and "ADMIN" not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot edit historical daily updates from past dates."
                )
            existing.status_id = payload.status_id
            existing.progress_percentage = payload.progress_percentage
            existing.remarks = payload.remarks
            saved = self.update_repo.update(existing)
        else:
            new_update = DailyTaskUpdate(
                task_id=payload.task_id,
                user_id=current_user.id,
                status_id=payload.status_id,
                update_date=target_date,
                progress_percentage=payload.progress_percentage,
                remarks=payload.remarks
            )
            saved = self.update_repo.create(new_update)

        return self._to_response(saved)

    def list_updates(
        self,
        current_user: User,
        user_roles: list[str],
        task_id: Optional[str] = None,
        target_user_id: Optional[str] = None,
        update_date: Optional[date] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status_id: Optional[int] = None
    ) -> list[DailyUpdateResponse]:
        filter_user_id = target_user_id
        filter_user_ids = None

        if "ADMIN" in user_roles:
            # Admin can view all or any target user
            pass
        elif "MANAGER" in user_roles:
            # Manager can view their subordinates and themselves
            subs = self.user_repo.list_all(manager_id=current_user.id)
            allowed_ids = [s.id for s in subs] + [current_user.id]
            if filter_user_id:
                if filter_user_id not in allowed_ids:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view updates for employees outside your team")
            else:
                filter_user_ids = allowed_ids
        else:
            # Employee can only view their own updates
            filter_user_id = current_user.id

        updates = self.update_repo.list_updates(
            task_id=task_id,
            user_id=filter_user_id,
            user_ids=filter_user_ids,
            update_date=update_date,
            from_date=from_date,
            to_date=to_date,
            status_id=status_id
        )
        return [self._to_response(u) for u in updates]

    def _to_response(self, update: DailyTaskUpdate) -> DailyUpdateResponse:
        return DailyUpdateResponse(
            id=update.id,
            task_id=update.task_id,
            task_title=update.task.title if update.task else None,
            task_priority=update.task.priority if update.task else None,
            task_due_date=update.task.due_date if update.task else None,
            user_id=update.user_id,
            user_name=update.user.name if update.user else None,
            user_employee_id=update.user.employee_id if update.user else None,
            status_id=update.status_id,
            status_name=update.status.name if update.status else None,
            update_date=update.update_date,
            progress_percentage=update.progress_percentage,
            remarks=update.remarks,
            submitted_at=update.submitted_at,
            updated_at=update.updated_at
        )
