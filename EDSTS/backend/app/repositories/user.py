from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).options(
            joinedload(User.user_roles).joinedload(UserRole.role),
            joinedload(User.manager)
        ).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).options(
            joinedload(User.user_roles).joinedload(UserRole.role)
        ).filter(User.email == email).first()

    def get_by_employee_id(self, employee_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.employee_id == employee_id).first()

    def list_all(self, manager_id: Optional[str] = None, department: Optional[str] = None, is_active: Optional[bool] = None) -> list[User]:
        query = self.db.query(User).options(
            joinedload(User.user_roles).joinedload(UserRole.role),
            joinedload(User.manager)
        )
        if manager_id:
            query = query.filter(User.manager_id == manager_id)
        if department:
            query = query.filter(User.department == department)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        return query.order_by(User.name.asc()).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == role_name).first()

    def list_roles(self) -> list[Role]:
        return self.db.query(Role).filter(Role.is_active == True).all()

    def add_user_role(self, user_id: str, role_id: int) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        self.db.commit()
        return user_role

    def remove_user_roles(self, user_id: str):
        self.db.query(UserRole).filter(UserRole.user_id == user_id).delete()
        self.db.commit()
