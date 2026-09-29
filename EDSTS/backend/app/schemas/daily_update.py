from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator

class DailyUpdateCreate(BaseModel):
    task_id: str
    status_id: int
    update_date: date = Field(default_factory=date.today)
    progress_percentage: int = Field(..., ge=0, le=100)
    remarks: str = Field(..., min_length=3)

    @model_validator(mode="after")
    def validate_status_and_progress(self):
        # We can add business rule validations (e.g. Completed -> 100%, Not Started -> 0%)
        return self

class DailyUpdateUpdate(BaseModel):
    status_id: int | None = None
    progress_percentage: int | None = Field(None, ge=0, le=100)
    remarks: str | None = Field(None, min_length=3)

class DailyUpdateResponse(BaseModel):
    id: str
    task_id: str
    task_title: str | None = None
    task_priority: str | None = None
    task_due_date: date | None = None
    user_id: str
    user_name: str | None = None
    user_employee_id: str | None = None
    status_id: int
    status_name: str | None = None
    update_date: date
    progress_percentage: int
    remarks: str
    submitted_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
