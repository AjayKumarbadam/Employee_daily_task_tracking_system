import sys
import os
from datetime import date, timedelta

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal
from app.services.auth import AuthService
from app.services.user import UserService
from app.services.task import TaskService
from app.services.daily_update import DailyUpdateService
from app.services.dashboard import DashboardService
from app.schemas.auth import LoginRequest
from app.schemas.task import TaskCreate
from app.schemas.daily_update import DailyUpdateCreate
from fastapi import HTTPException

def run_all_tests():
    db = SessionLocal()
    try:
        print("=== RUNNING EDSTS BACKEND VERIFICATION SUITE ===")

        # 1. Test Authentication
        print("\n[TEST 1] Testing Authentication Service...")
        auth_service = AuthService(db)
        
        # Valid Admin Login
        admin_res = auth_service.authenticate_user(LoginRequest(email="admin@edsts.com", password="admin123"))
        assert "access_token" in admin_res
        assert "ADMIN" in admin_res["user"]["roles"]
        print("  [PASS] Admin login succeeded and returned JWT token")

        # Valid Manager Login
        mgr_res = auth_service.authenticate_user(LoginRequest(email="manager@edsts.com", password="manager123"))
        assert "MANAGER" in mgr_res["user"]["roles"]
        print("  [PASS] Manager login succeeded")

        # Valid Employee Login
        ravi_res = auth_service.authenticate_user(LoginRequest(email="ravi@edsts.com", password="ravi123"))
        assert "EMPLOYEE" in ravi_res["user"]["roles"]
        print("  [PASS] Employee (Ravi) login succeeded")

        # Invalid password check
        try:
            auth_service.authenticate_user(LoginRequest(email="ravi@edsts.com", password="wrongpassword"))
            assert False, "Should have raised 401"
        except HTTPException as e:
            assert e.status_code == 401
            print("  [PASS] Invalid password correctly rejected with 401 Unauthorized")

        # 2. Test Task Service & Role-Based Access
        print("\n[TEST 2] Testing Task Management & RBAC...")
        user_service = UserService(db)
        task_service = TaskService(db)
        
        ravi_user = user_service.user_repo.get_by_email("ravi@edsts.com")
        priya_user = user_service.user_repo.get_by_email("priya@edsts.com")
        manager_user = user_service.user_repo.get_by_email("manager@edsts.com")

        # Employee (Ravi) lists his tasks
        ravi_tasks = task_service.list_tasks(current_user=ravi_user, user_roles=["EMPLOYEE"])
        assert len(ravi_tasks) >= 3
        print(f"  [PASS] Ravi retrieved {len(ravi_tasks)} assigned tasks")

        # 3. Test Ownership Verification on Daily Update
        print("\n[TEST 3] Testing Ownership and Business Rule Constraints...")
        daily_service = DailyUpdateService(db)
        statuses = {s.name: s.id for s in task_service.task_repo.list_statuses()}

        priya_tasks = task_service.list_tasks(current_user=priya_user, user_roles=["EMPLOYEE"])
        priya_task_id = priya_tasks[0].id

        # Ownership violation: Ravi tries to submit update for Priya's task
        try:
            daily_service.submit_daily_update(
                DailyUpdateCreate(
                    task_id=priya_task_id,
                    status_id=statuses["IN_PROGRESS"],
                    progress_percentage=50,
                    remarks="Unauthorized submission"
                ),
                current_user=ravi_user,
                user_roles=["EMPLOYEE"]
            )
            assert False, "Should have raised 403 Forbidden"
        except HTTPException as e:
            assert e.status_code == 403
            print("  [PASS] Ownership check blocked unauthorized cross-employee update (403 Forbidden)")

        # Status validation: Completed status must be 100%
        try:
            daily_service.submit_daily_update(
                DailyUpdateCreate(
                    task_id=ravi_tasks[0].id,
                    status_id=statuses["COMPLETED"],
                    progress_percentage=75,
                    remarks="Invalid percentage for completed"
                ),
                current_user=ravi_user,
                user_roles=["EMPLOYEE"]
            )
            assert False, "Should have raised 400 Bad Request"
        except HTTPException as e:
            assert e.status_code == 400
            print("  [PASS] Validation check enforced 100% for COMPLETED status")

        # 4. Test Manager & Employee Dashboard Service
        print("\n[TEST 4] Testing Dashboard Statistics Calculation...")
        dash_service = DashboardService(db)
        mgr_dash = dash_service.get_manager_dashboard(current_user=manager_user, user_roles=["MANAGER"])
        assert mgr_dash.summary.total_tasks > 0
        assert len(mgr_dash.employees) >= 3
        print(f"  [PASS] Manager Dashboard: {mgr_dash.summary.total_tasks} Total Tasks, {mgr_dash.summary.completed} Completed, {mgr_dash.summary.in_progress} In Progress")

        emp_dash = dash_service.get_employee_dashboard(current_user=ravi_user)
        assert emp_dash.summary.total_tasks >= 3
        print(f"  [PASS] Employee Dashboard: {emp_dash.summary.total_tasks} Tasks, {emp_dash.today_submitted_count} submitted today")

        print("=======================================================")
        print("[SUCCESS] ALL BACKEND BUSINESS LOGIC & CONSTRAINTS PASSED 100%!")
        print("=======================================================\n")
    finally:
        db.close()

if __name__ == "__main__":
    run_all_tests()
