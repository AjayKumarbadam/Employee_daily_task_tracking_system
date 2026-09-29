from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.user import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.dependencies import get_current_user, get_current_user_roles, require_role, require_any_role
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=list[UserResponse])
def get_users(
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    if "ADMIN" in roles:
        return user_service.list_users(department=department, is_active=is_active)
    elif "MANAGER" in roles:
        # Managers can view all active users to assign tasks or see subordinates
        return user_service.list_users(department=department, is_active=is_active)
    else:
        # Employees can view basic user directory for lookup
        return user_service.list_users(is_active=True)

@router.get("/subordinates", response_model=list[UserResponse])
def get_subordinates(
    current_user: User = Depends(require_any_role(["ADMIN", "MANAGER"])),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    if "ADMIN" in roles:
        return user_service.list_users()
    return user_service.list_users(manager_id=current_user.id)

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    if "ADMIN" not in roles and "MANAGER" not in roles and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.create_user(user_data)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    roles: list[str] = Depends(get_current_user_roles),
    db: Session = Depends(get_db)
):
    if "ADMIN" not in roles and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit other user's profile")
    
    # Non-admin cannot change their own roles or active status
    if "ADMIN" not in roles:
        user_data.roles = None
        user_data.is_active = None
        user_data.manager_id = None

    user_service = UserService(db)
    return user_service.update_user(user_id, user_data)

@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.set_active_status(user_id, is_active=False)

@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.set_active_status(user_id, is_active=True)
