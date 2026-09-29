from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.dashboard import DashboardService
from app.schemas.dashboard import ManagerDashboardResponse, EmployeeDashboardResponse
from app.dependencies import get_current_user, get_current_user_roles, require_any_role
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Metrics"])

@router.get("/manager", response_model=ManagerDashboardResponse)
def get_manager_dashboard(
    target_date: Optional[date] = None,
    current_user: User = Depends(require_any_role(["ADMIN", "MANAGER"])),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    service = DashboardService(db)
    return service.get_manager_dashboard(current_user, roles, target_date)

@router.get("/employee", response_model=EmployeeDashboardResponse)
def get_employee_dashboard(
    target_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DashboardService(db)
    return service.get_employee_dashboard(current_user, target_date)
