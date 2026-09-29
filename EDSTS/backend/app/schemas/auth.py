from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None
    roles: list[str] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    password: str
    department: str
    designation: str
    manager_id: str | None = None
    roles: list[str] = ["EMPLOYEE"]
