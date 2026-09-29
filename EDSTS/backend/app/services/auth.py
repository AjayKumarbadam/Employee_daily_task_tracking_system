from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.shared.security import verify_password, create_access_token, hash_password
from app.schemas.auth import LoginRequest, RegisterRequest
from app.models.user import User

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate_user(self, login_data: LoginRequest) -> dict:
        user = self.user_repo.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated. Please contact your administrator.",
            )

        roles = [ur.role.name for ur in user.user_roles] if user.user_roles else ["EMPLOYEE"]
        
        token_payload = {
            "sub": user.id,
            "email": user.email,
            "roles": roles,
            "name": user.name
        }
        access_token = create_access_token(data=token_payload)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "employee_id": user.employee_id,
                "name": user.name,
                "email": user.email,
                "department": user.department,
                "designation": user.designation,
                "manager_id": user.manager_id,
                "roles": roles,
                "is_active": user.is_active
            }
        }

    def register_user(self, reg_data: RegisterRequest) -> User:
        if self.user_repo.get_by_email(reg_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

        if self.user_repo.get_by_employee_id(reg_data.employee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists."
            )

        new_user = User(
            employee_id=reg_data.employee_id,
            name=reg_data.name,
            email=reg_data.email,
            password_hash=hash_password(reg_data.password),
            department=reg_data.department,
            designation=reg_data.designation,
            manager_id=reg_data.manager_id,
            is_active=True
        )
        created_user = self.user_repo.create(new_user)

        # Assign roles
        for role_name in reg_data.roles:
            role = self.user_repo.get_role_by_name(role_name)
            if role:
                self.user_repo.add_user_role(created_user.id, role.id)

        return self.user_repo.get_by_id(created_user.id)
