from typing import Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.models.daily_task_update import DailyTaskUpdate
from app.models.task import Task
from app.models.user import User

class DailyUpdateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, update_id: str) -> Optional[DailyTaskUpdate]:
        return self.db.query(DailyTaskUpdate).options(
            joinedload(DailyTaskUpdate.task),
            joinedload(DailyTaskUpdate.user),
            joinedload(DailyTaskUpdate.status)
        ).filter(DailyTaskUpdate.id == update_id).first()

    def get_by_task_user_date(self, task_id: str, user_id: str, update_date: date) -> Optional[DailyTaskUpdate]:
        return self.db.query(DailyTaskUpdate).options(
            joinedload(DailyTaskUpdate.status),
            joinedload(DailyTaskUpdate.task),
            joinedload(DailyTaskUpdate.user)
        ).filter(
            DailyTaskUpdate.task_id == task_id,
            DailyTaskUpdate.user_id == user_id,
            DailyTaskUpdate.update_date == update_date
        ).first()

    def list_updates(
        self,
        task_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_ids: Optional[list[str]] = None,
        update_date: Optional[date] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        status_id: Optional[int] = None
    ) -> list[DailyTaskUpdate]:
        query = self.db.query(DailyTaskUpdate).options(
            joinedload(DailyTaskUpdate.task),
            joinedload(DailyTaskUpdate.user),
            joinedload(DailyTaskUpdate.status)
        )

        if task_id:
            query = query.filter(DailyTaskUpdate.task_id == task_id)
        if user_id:
            query = query.filter(DailyTaskUpdate.user_id == user_id)
        elif user_ids is not None:
            query = query.filter(DailyTaskUpdate.user_id.in_(user_ids))
        if update_date:
            query = query.filter(DailyTaskUpdate.update_date == update_date)
        if from_date:
            query = query.filter(DailyTaskUpdate.update_date >= from_date)
        if to_date:
            query = query.filter(DailyTaskUpdate.update_date <= to_date)
        if status_id:
            query = query.filter(DailyTaskUpdate.status_id == status_id)

        return query.order_by(DailyTaskUpdate.update_date.desc(), DailyTaskUpdate.submitted_at.desc()).all()

    def create(self, update: DailyTaskUpdate) -> DailyTaskUpdate:
        self.db.add(update)
        self.db.commit()
        self.db.refresh(update)
        return update

    def update(self, update: DailyTaskUpdate) -> DailyTaskUpdate:
        self.db.commit()
        self.db.refresh(update)
        return update
