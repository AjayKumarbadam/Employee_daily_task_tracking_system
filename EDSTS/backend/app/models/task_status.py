from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

class TaskStatus(Base):
    __tablename__ = "task_statuses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True) # NOT_STARTED, IN_PROGRESS, COMPLETED, BLOCKED, CANCELLED
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    daily_updates = relationship("DailyTaskUpdate", back_populates="status")
