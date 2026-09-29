from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.shared.security import hash_password

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user_by_id(self, user_id: str) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return self._to_response(user)

    def list_users(self, manager_id: Optional[str] = None, department: Optional[str] = None, is_active: Optional[bool] = None) -> list[UserResponse]:
        users = self.user_repo.list_all(manager_id=manager_id, department=department, is_active=is_active)
        return [self._to_response(u) for u in users]

    def create_user(self, user_data: UserCreate) -> UserResponse:
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if self.user_repo.get_by_employee_id(user_data.employee_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Employee ID already exists")

        user = User(
            employee_id=user_data.employee_id,
            name=user_data.name,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            department=user_data.department,
            designation=user_data.designation,
            manager_id=user_data.manager_id,
            is_active=user_data.is_active
        )
        created = self.user_repo.create(user)

        for r_name in user_data.roles:
            role = self.user_repo.get_role_by_name(r_name)
            if role:
                self.user_repo.add_user_role(created.id, role.id)

        return self.get_user_by_id(created.id)

    def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None and user_data.email != user.email:
            existing = self.user_repo.get_by_email(user_data.email)
            if existing and existing.id != user.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already taken")
            user.email = user_data.email
        if user_data.department is not None:
            user.department = user_data.department
        if user_data.designation is not None:
            user.designation = user_data.designation
        if user_data.manager_id is not None:
            user.manager_id = user_data.manager_id if user_data.manager_id != "" else None
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        if user_data.password:
            user.password_hash = hash_password(user_data.password)

        if user_data.roles is not None:
            self.user_repo.remove_user_roles(user.id)
            for r_name in user_data.roles:
                role = self.user_repo.get_role_by_name(r_name)
                if role:
                    self.user_repo.add_user_role(user.id, role.id)

        self.user_repo.update(user)
        return self.get_user_by_id(user.id)

    def set_active_status(self, user_id: str, is_active: bool) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.is_active = is_active
        self.user_repo.update(user)
        return self.get_user_by_id(user.id)

    def _to_response(self, user: User) -> UserResponse:
        roles = [ur.role.name for ur in user.user_roles if ur.role] if user.user_roles else []
        manager_data = None
        if user.manager:
            manager_data = {
                "id": user.manager.id,
                "name": user.manager.name,
                "employee_id": user.manager.employee_id,
                "email": user.manager.email
            }
        return UserResponse(
            id=user.id,
            employee_id=user.employee_id,
            name=user.name,
            email=user.email,
            department=user.department,
            designation=user.designation,
            manager_id=user.manager_id,
            manager=manager_data,
            is_active=user.is_active,
            roles=roles,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
