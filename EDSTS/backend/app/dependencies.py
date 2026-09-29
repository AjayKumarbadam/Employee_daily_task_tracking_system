from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.repositories.user import UserRepository
from app.models.user import User
from app.shared.security import decode_access_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User associated with token does not exist",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user

def get_current_user_roles(user: User = Depends(get_current_user)) -> list[str]:
    if not user.user_roles:
        return ["EMPLOYEE"]
    return [ur.role.name for ur in user.user_roles if ur.role]

def require_role(required_role: str) -> Callable:
    def role_checker(
        current_user: User = Depends(get_current_user),
        roles: list[str] = Depends(get_current_user_roles)
    ) -> User:
        if "ADMIN" in roles: # Admin superuser override
            return current_user
        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {required_role}",
            )
        return current_user
    return role_checker

def require_any_role(required_roles: list[str]) -> Callable:
    def role_checker(
        current_user: User = Depends(get_current_user),
        roles: list[str] = Depends(get_current_user_roles)
    ) -> User:
        if "ADMIN" in roles:
            return current_user
        if not any(r in roles for r in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required one of roles: {', '.join(required_roles)}",
            )
        return current_user
    return role_checker
