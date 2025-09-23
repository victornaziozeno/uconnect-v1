from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .db import Base

# ---------------- ENUMS ---------------- #

class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    coordinator = "coordinator"
    contractor = "contract"
    admin = "admin"

class AccessStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

# ---------------- USER & SESSION ---------------- #

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .db import Base

class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    coordinator = "coordinator"
    contractor = "contract"
    admin = "admin"

class AccessStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    registration = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    passwordHash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    accessStatus = Column(Enum(AccessStatus), default=AccessStatus.active, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_users_registration", "registration"),
        Index("ix_users_email", "email"),
    )

class Session(Base):
    __tablename__ = "Session"
    token = Column(String(500), primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("User.id"), nullable=False, index=True)
    startDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    expirationDate = Column(DateTime, nullable=False)

    user = relationship("User", lazy="joined")