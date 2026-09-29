from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.repositories.task import TaskRepository
from app.repositories.daily_update import DailyUpdateRepository
from app.models.user import User
from app.schemas.dashboard import (
    ManagerDashboardResponse,
    EmployeeDashboardResponse,
    DashboardSummary,
    EmployeeStatusCount
)

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.task_repo = TaskRepository(db)
        self.update_repo = DailyUpdateRepository(db)

    def get_manager_dashboard(self, current_user: User, user_roles: list[str], target_date: Optional[date] = None) -> ManagerDashboardResponse:
        calc_date = target_date or date.today()

        # Get relevant employees
        if "ADMIN" in user_roles:
            employees = self.user_repo.list_all(is_active=True)
        else:
            employees = self.user_repo.list_all(manager_id=current_user.id, is_active=True)

        emp_ids = [e.id for e in employees]

        # Calculate counts per employee
        employee_counts: list[EmployeeStatusCount] = []
        tot_tasks = 0
        tot_completed = 0
        tot_in_progress = 0
        tot_not_started = 0
        tot_blocked = 0
        tot_cancelled = 0
        tot_overdue = 0

        for emp in employees:
            emp_tasks = self.task_repo.list_tasks(assigned_user_id=emp.id)
            emp_updates = self.update_repo.list_updates(user_id=emp.id, update_date=calc_date)
            update_map = {u.task_id: u for u in emp_updates}

            comp = 0
            in_prog = 0
            not_start = 0
            block = 0
            canc = 0

            for t in emp_tasks:
                # If there's an update on calc_date, use that; otherwise use latest update
                status_name = "NOT_STARTED"
                if t.id in update_map:
                    status_name = update_map[t.id].status.name if update_map[t.id].status else "NOT_STARTED"
                elif t.daily_updates:
                    sorted_u = sorted(t.daily_updates, key=lambda x: (x.update_date, x.submitted_at), reverse=True)
                    status_name = sorted_u[0].status.name if sorted_u[0].status else "NOT_STARTED"

                if status_name == "COMPLETED":
                    comp += 1
                elif status_name == "IN_PROGRESS":
                    in_prog += 1
                elif status_name == "BLOCKED":
                    block += 1
                elif status_name == "CANCELLED":
                    canc += 1
                else:
                    not_start += 1

                if t.due_date < calc_date and status_name != "COMPLETED":
                    tot_overdue += 1

            has_submitted = len(emp_updates) > 0 if len(emp_tasks) > 0 else True

            tot_tasks += len(emp_tasks)
            tot_completed += comp
            tot_in_progress += in_prog
            tot_not_started += not_start
            tot_blocked += block
            tot_cancelled += canc

            employee_counts.append(
                EmployeeStatusCount(
                    user_id=emp.id,
                    employee_id=emp.employee_id,
                    name=emp.name,
                    department=emp.department,
                    completed=comp,
                    in_progress=in_prog,
                    not_started=not_start,
                    blocked=block,
                    total_assigned=len(emp_tasks),
                    has_submitted_today=has_submitted
                )
            )

        summary = DashboardSummary(
            total_tasks=tot_tasks,
            completed=tot_completed,
            in_progress=tot_in_progress,
            not_started=tot_not_started,
            blocked=tot_blocked,
            cancelled=tot_cancelled,
            overdue=tot_overdue
        )

        return ManagerDashboardResponse(
            summary_date=calc_date,
            summary=summary,
            employees=employee_counts
        )

    def get_employee_dashboard(self, current_user: User, target_date: Optional[date] = None) -> EmployeeDashboardResponse:
        calc_date = target_date or date.today()
        emp_tasks = self.task_repo.list_tasks(assigned_user_id=current_user.id)
        emp_updates = self.update_repo.list_updates(user_id=current_user.id, update_date=calc_date)
        update_map = {u.task_id: u for u in emp_updates}

        comp = 0
        in_prog = 0
        not_start = 0
        block = 0
        canc = 0
        overdue = 0

        for t in emp_tasks:
            status_name = "NOT_STARTED"
            if t.id in update_map:
                status_name = update_map[t.id].status.name if update_map[t.id].status else "NOT_STARTED"
            elif t.daily_updates:
                sorted_u = sorted(t.daily_updates, key=lambda x: (x.update_date, x.submitted_at), reverse=True)
                status_name = sorted_u[0].status.name if sorted_u[0].status else "NOT_STARTED"

            if status_name == "COMPLETED":
                comp += 1
            elif status_name == "IN_PROGRESS":
                in_prog += 1
            elif status_name == "BLOCKED":
                block += 1
            elif status_name == "CANCELLED":
                canc += 1
            else:
                not_start += 1

            if t.due_date < calc_date and status_name != "COMPLETED":
                overdue += 1

        submitted_count = len(emp_updates)
        pending_count = max(0, len(emp_tasks) - submitted_count)

        summary = DashboardSummary(
            total_tasks=len(emp_tasks),
            completed=comp,
            in_progress=in_prog,
            not_started=not_start,
            blocked=block,
            cancelled=canc,
            overdue=overdue
        )

        return EmployeeDashboardResponse(
            summary_date=calc_date,
            summary=summary,
            today_submitted_count=submitted_count,
            today_pending_count=pending_count
        )
