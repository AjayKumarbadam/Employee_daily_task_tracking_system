import sys
import os
from datetime import date, timedelta

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal, engine, Base
from app.models.role import Role
from app.models.task_status import TaskStatus
from app.models.user import User
from app.models.user_role import UserRole
from app.models.task import Task
from app.models.task_assignment import TaskAssignment
from app.models.daily_task_update import DailyTaskUpdate
from app.shared.security import hash_password

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("[*] Seeding Database...")

        # 1. Seed Roles
        roles_data = [
            ("ADMIN", "System Administrator with full access"),
            ("MANAGER", "Team Manager who can assign tasks and review progress"),
            ("EMPLOYEE", "Individual Contributor who works on tasks and submits daily status")
        ]
        role_map = {}
        for r_name, r_desc in roles_data:
            existing_role = db.query(Role).filter(Role.name == r_name).first()
            if not existing_role:
                role = Role(name=r_name, description=r_desc, is_active=True)
                db.add(role)
                db.commit()
                db.refresh(role)
                role_map[r_name] = role
                print(f"  + Added Role: {r_name}")
            else:
                role_map[r_name] = existing_role

        # 2. Seed Task Statuses
        statuses_data = [
            ("NOT_STARTED", "Task has not been started yet"),
            ("IN_PROGRESS", "Task is currently being actively worked on"),
            ("COMPLETED", "Task work is 100% finished and verified"),
            ("BLOCKED", "Task is blocked due to external dependency or obstacle"),
            ("CANCELLED", "Task has been cancelled")
        ]
        status_map = {}
        for s_name, s_desc in statuses_data:
            existing_s = db.query(TaskStatus).filter(TaskStatus.name == s_name).first()
            if not existing_s:
                st = TaskStatus(name=s_name, description=s_desc, is_active=True)
                db.add(st)
                db.commit()
                db.refresh(st)
                status_map[s_name] = st
                print(f"  + Added Status: {s_name}")
            else:
                status_map[s_name] = existing_s

        # 3. Seed Users
        # Admin
        admin = db.query(User).filter(User.email == "admin@edsts.com").first()
        if not admin:
            admin = User(
                employee_id="ADM001",
                name="Suresh Kumar (Admin)",
                email="admin@edsts.com",
                password_hash=hash_password("admin123"),
                department="Management",
                designation="Director of Engineering",
                is_active=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            db.add(UserRole(user_id=admin.id, role_id=role_map["ADMIN"].id))
            db.commit()
            print("  + Added Admin: admin@edsts.com / admin123")

        # Manager
        manager = db.query(User).filter(User.email == "manager@edsts.com").first()
        if not manager:
            manager = User(
                employee_id="MGR101",
                name="Vikas Sharma (Manager)",
                email="manager@edsts.com",
                password_hash=hash_password("manager123"),
                department="Engineering",
                designation="Engineering Manager",
                manager_id=admin.id,
                is_active=True
            )
            db.add(manager)
            db.commit()
            db.refresh(manager)
            db.add(UserRole(user_id=manager.id, role_id=role_map["MANAGER"].id))
            db.commit()
            print("  + Added Manager: manager@edsts.com / manager123")

        # Employees
        employees_data = [
            ("EMP201", "Ravi Kumar", "ravi@edsts.com", "ravi123", "Engineering", "Senior Backend Engineer"),
            ("EMP202", "Priya Patel", "priya@edsts.com", "priya123", "Engineering", "Frontend Developer"),
            ("EMP203", "Arun Verma", "arun@edsts.com", "arun123", "Engineering", "Fullstack Developer")
        ]
        emp_map = {}
        for eid, ename, email, pwd, dept, desig in employees_data:
            existing_emp = db.query(User).filter(User.email == email).first()
            if not existing_emp:
                emp = User(
                    employee_id=eid,
                    name=ename,
                    email=email,
                    password_hash=hash_password(pwd),
                    department=dept,
                    designation=desig,
                    manager_id=manager.id,
                    is_active=True
                )
                db.add(emp)
                db.commit()
                db.refresh(emp)
                db.add(UserRole(user_id=emp.id, role_id=role_map["EMPLOYEE"].id))
                db.commit()
                emp_map[email] = emp
                print(f"  + Added Employee: {email} / {pwd}")
            else:
                emp_map[email] = existing_emp

        # 4. Seed Tasks & Assignments
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        two_days_later = today + timedelta(days=2)

        ravi = emp_map.get("ravi@edsts.com")
        priya = emp_map.get("priya@edsts.com")
        arun = emp_map.get("arun@edsts.com")

        if ravi:
            # Task 1: Authentication API (Due: Today, Priority: HIGH)
            t1 = db.query(Task).filter(Task.title == "Authentication API").first()
            if not t1:
                t1 = Task(
                    title="Authentication API",
                    description="Implement JWT authentication, login endpoint, token expiration and password hashing.",
                    priority="HIGH",
                    due_date=today,
                    created_by=manager.id
                )
                db.add(t1)
                db.commit()
                db.refresh(t1)
                db.add(TaskAssignment(task_id=t1.id, user_id=ravi.id, assigned_by=manager.id, is_active=True))
                db.commit()

                # Ravi's update today
                db.add(DailyTaskUpdate(
                    task_id=t1.id,
                    user_id=ravi.id,
                    status_id=status_map["COMPLETED"].id,
                    update_date=today,
                    progress_percentage=100,
                    remarks="JWT authentication implemented and tested."
                ))
                db.commit()
                print("  + Added Task & Update: Authentication API (Ravi -> COMPLETED 100%)")

            # Task 2: Authorization API (Due: Tomorrow, Priority: MEDIUM)
            t2 = db.query(Task).filter(Task.title == "Authorization API").first()
            if not t2:
                t2 = Task(
                    title="Authorization API",
                    description="Role and permission checks across protected endpoints with ownership rules.",
                    priority="MEDIUM",
                    due_date=tomorrow,
                    created_by=manager.id
                )
                db.add(t2)
                db.commit()
                db.refresh(t2)
                db.add(TaskAssignment(task_id=t2.id, user_id=ravi.id, assigned_by=manager.id, is_active=True))
                db.commit()

                # Historical yesterday update (IN_PROGRESS 30%)
                db.add(DailyTaskUpdate(
                    task_id=t2.id,
                    user_id=ravi.id,
                    status_id=status_map["IN_PROGRESS"].id,
                    update_date=yesterday,
                    progress_percentage=30,
                    remarks="Started role structure and DB schema models."
                ))
                # Today update (IN_PROGRESS 60%)
                db.add(DailyTaskUpdate(
                    task_id=t2.id,
                    user_id=ravi.id,
                    status_id=status_map["IN_PROGRESS"].id,
                    update_date=today,
                    progress_percentage=60,
                    remarks="Role and permission checks completed. Endpoint authorization remaining."
                ))
                db.commit()
                print("  + Added Task & Updates: Authorization API (Ravi -> IN_PROGRESS 60%)")

            # Task 3: Database Design (Due: Two days later, Priority: HIGH)
            t3 = db.query(Task).filter(Task.title == "Database Design & Optimization").first()
            if not t3:
                t3 = Task(
                    title="Database Design & Optimization",
                    description="Optimize indexes and create ERD documentation for production schemas.",
                    priority="HIGH",
                    due_date=two_days_later,
                    created_by=manager.id
                )
                db.add(t3)
                db.commit()
                db.refresh(t3)
                db.add(TaskAssignment(task_id=t3.id, user_id=ravi.id, assigned_by=manager.id, is_active=True))
                db.commit()

                db.add(DailyTaskUpdate(
                    task_id=t3.id,
                    user_id=ravi.id,
                    status_id=status_map["NOT_STARTED"].id,
                    update_date=today,
                    progress_percentage=0,
                    remarks="Will start tomorrow after authorization API completion."
                ))
                db.commit()
                print("  + Added Task & Update: Database Design (Ravi -> NOT_STARTED 0%)")

        if priya:
            # Priya's Task: React Dashboard UI
            tp = db.query(Task).filter(Task.title == "React Dashboard UI").first()
            if not tp:
                tp = Task(
                    title="React Dashboard UI",
                    description="Build responsive manager and employee dashboard widgets with status cards.",
                    priority="HIGH",
                    due_date=today,
                    created_by=manager.id
                )
                db.add(tp)
                db.commit()
                db.refresh(tp)
                db.add(TaskAssignment(task_id=tp.id, user_id=priya.id, assigned_by=manager.id, is_active=True))
                db.commit()

                db.add(DailyTaskUpdate(
                    task_id=tp.id,
                    user_id=priya.id,
                    status_id=status_map["IN_PROGRESS"].id,
                    update_date=today,
                    progress_percentage=75,
                    remarks="Dashboard summary cards, charts and responsive layout completed."
                ))
                db.commit()

        if arun:
            # Arun's Task: API Integration & Testing
            ta = db.query(Task).filter(Task.title == "API Integration & End-to-End Tests").first()
            if not ta:
                ta = Task(
                    title="API Integration & End-to-End Tests",
                    description="Write pytest suite for all endpoints and verify cross-role access.",
                    priority="MEDIUM",
                    due_date=tomorrow,
                    created_by=manager.id
                )
                db.add(ta)
                db.commit()
                db.refresh(ta)
                db.add(TaskAssignment(task_id=ta.id, user_id=arun.id, assigned_by=manager.id, is_active=True))
                db.commit()

                db.add(DailyTaskUpdate(
                    task_id=ta.id,
                    user_id=arun.id,
                    status_id=status_map["BLOCKED"].id,
                    update_date=today,
                    progress_percentage=40,
                    remarks="Blocked waiting for staging server CORS headers update."
                ))
                db.commit()

        print("[+] Database seeding completed successfully!")
    except Exception as e:
        print(f"[-] Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
