from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.daily_update import DailyUpdateService
from app.schemas.daily_update import DailyUpdateCreate, DailyUpdateResponse
from app.dependencies import get_current_user, get_current_user_roles
from app.models.user import User

router = APIRouter(prefix="/daily-updates", tags=["Daily Task Updates"])

@router.post("", response_model=DailyUpdateResponse, status_code=status.HTTP_201_CREATED)
def submit_daily_update(
    update_data: DailyUpdateCreate,
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    service = DailyUpdateService(db)
    return service.submit_daily_update(update_data, current_user, roles)

@router.get("", response_model=list[DailyUpdateResponse])
def get_daily_updates(
    task_id: Optional[str] = None,
    user_id: Optional[str] = None,
    update_date: Optional[date] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    status_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    service = DailyUpdateService(db)
    return service.list_updates(
        current_user=current_user,
        user_roles=roles,
        task_id=task_id,
        target_user_id=user_id,
        update_date=update_date,
        from_date=from_date,
        to_date=to_date,
        status_id=status_id
    )

@router.get("/today", response_model=list[DailyUpdateResponse])
def get_today_updates(
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    service = DailyUpdateService(db)
    return service.list_updates(
        current_user=current_user,
        user_roles=roles,
        update_date=date.today()
    )
