from datetime import date, datetime
from pydantic import BaseModel, Field
from app.shared.enums import PriorityEnum

class TaskStatusResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str | None = None
    priority: PriorityEnum = PriorityEnum.MEDIUM
    due_date: date

class TaskCreate(TaskBase):
    assigned_to_user_id: str | None = None # Optional initial assignment during creation

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=200)
    description: str | None = None
    priority: PriorityEnum | None = None
    due_date: date | None = None

class TaskAssignRequest(BaseModel):
    user_id: str

class UserBrief(BaseModel):
    id: str
    employee_id: str
    name: str
    email: str
    department: str

    class Config:
        from_attributes = True

class TaskAssignmentResponse(BaseModel):
    id: str
    task_id: str
    user_id: str
    assignee: UserBrief
    assigned_by: str
    assigner: UserBrief | None = None
    assigned_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class LatestUpdateBrief(BaseModel):
    id: str
    status_id: int
    status_name: str
    progress_percentage: int
    remarks: str
    update_date: date
    submitted_at: datetime

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    priority: str
    due_date: date
    created_by: str
    creator: UserBrief | None = None
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False
    current_assignment: TaskAssignmentResponse | None = None
    latest_update: LatestUpdateBrief | None = None

    class Config:
        from_attributes = True
