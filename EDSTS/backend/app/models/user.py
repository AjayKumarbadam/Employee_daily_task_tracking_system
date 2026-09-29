import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    manager_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    manager = relationship("User", remote_side=[id], backref="subordinates")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    assignments = relationship("TaskAssignment", foreign_keys="TaskAssignment.user_id", back_populates="assignee")
    assigned_by_me = relationship("TaskAssignment", foreign_keys="TaskAssignment.assigned_by", back_populates="assigner")
    daily_updates = relationship("DailyTaskUpdate", back_populates="user", cascade="all, delete-orphan")
