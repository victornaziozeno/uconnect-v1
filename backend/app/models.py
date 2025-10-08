from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, Enum, ForeignKey, Text, Index, Time
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .db import Base

# ---------------- ENUMS ---------------- #
class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    coordinator = "coordinator"
    admin = "admin"

class AccessStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

# ---------------- AUTHENTICATION & ACCESS ---------------- #
class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True, index=True)
    registration = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    passwordHash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    accessStatus = Column(Enum(AccessStatus), default=AccessStatus.active, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    events_created = relationship("Event", back_populates="creator")

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

# ---------------- ACADEMIC MANAGEMENT ---------------- #
class Event(Base):
    __tablename__ = "Event"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Nova estrutura de data e horários (usando String para horários)
    timestamp = Column(DateTime, nullable=False)  # Data e hora completa para auditoria/ordenação
    eventDate = Column(Date, nullable=False)  # Data do evento
    startTime = Column(Time, nullable=True)
    endTime = Column(Time, nullable=True)

    academicGroupId = Column(String(50), nullable=True)
    creatorId = Column(Integer, ForeignKey("User.id", ondelete="SET NULL"), nullable=True)
    
    creator = relationship("User", back_populates="events_created")
    
    __table_args__ = (
        Index("idx_event_date", "eventDate"),
        Index("idx_event_timestamp", "timestamp"),
        Index("idx_event_creator", "creatorId"),
    )