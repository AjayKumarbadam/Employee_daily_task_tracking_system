import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.database import Base

class DailyTaskUpdate(Base):
    __tablename__ = "daily_task_updates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status_id = Column(Integer, ForeignKey("task_statuses.id", ondelete="RESTRICT"), nullable=False)
    update_date = Column(Date, nullable=False, index=True)
    progress_percentage = Column(Integer, nullable=False) # 0 to 100
    remarks = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("task_id", "user_id", "update_date", name="uq_task_user_date"),
    )

    task = relationship("Task", back_populates="daily_updates")
    user = relationship("User", back_populates="daily_updates")
    status = relationship("TaskStatus", back_populates="daily_updates")
