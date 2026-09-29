from datetime import date
from pydantic import BaseModel

class DashboardSummary(BaseModel):
    total_tasks: int
    completed: int
    in_progress: int
    not_started: int
    blocked: int
    cancelled: int
    overdue: int

class EmployeeStatusCount(BaseModel):
    user_id: str
    employee_id: str
    name: str
    department: str
    completed: int = 0
    in_progress: int = 0
    not_started: int = 0
    blocked: int = 0
    total_assigned: int = 0
    has_submitted_today: bool = False

class ManagerDashboardResponse(BaseModel):
    summary_date: date
    summary: DashboardSummary
    employees: list[EmployeeStatusCount]

class EmployeeDashboardResponse(BaseModel):
    summary_date: date
    summary: DashboardSummary
    today_submitted_count: int
    today_pending_count: int
