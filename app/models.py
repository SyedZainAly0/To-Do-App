from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Enum
import enum

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(70), nullable=False, unique=True)

    email = Column(String(100), nullable=False, unique=True)

    password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    tasks = relationship("Task", back_populates="owner", cascade="all, delete")


class PriorityEnum(str, enum.Enum):
    LOW = "LOW"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL",


class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(100), nullable=False)

    description = Column(String(250))

    is_completed = Column(Boolean, default=False)

    priority = Column(Enum(PriorityEnum), default=PriorityEnum.LOW)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner = relationship("User", back_populates="tasks")