from datetime import datetime
from pydantic import BaseModel, EmailStr

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    department: str
    designation: str
    manager_id: str | None = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    roles: list[str] = ["EMPLOYEE"]

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    department: str | None = None
    designation: str | None = None
    manager_id: str | None = None
    is_active: bool | None = None
    password: str | None = None
    roles: list[str] | None = None

class ManagerBrief(BaseModel):
    id: str
    name: str
    employee_id: str
    email: str

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: str
    employee_id: str
    name: str
    email: str
    department: str
    designation: str
    manager_id: str | None = None
    manager: ManagerBrief | None = None
    is_active: bool
    roles: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
