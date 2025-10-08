from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, Enum, ForeignKey, Text, Index, Time, Table
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

# ---------------- TABELA DE ASSOCIAÇÃO ---------------- #

academic_group_user_association = Table('AcademicGroup_User', Base.metadata,
    Column('groupId', Integer, ForeignKey('AcademicGroup.id'), primary_key=True),
    Column('userId', Integer, ForeignKey('User.id'), primary_key=True)
)

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
    groups = relationship(
        "AcademicGroup",
        secondary=academic_group_user_association,
        back_populates="users"
    )
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

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
    timestamp = Column(DateTime, nullable=False)  
    eventDate = Column(Date, nullable=False)  
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

class AcademicGroup(Base):
    __tablename__ = "AcademicGroup"

    id = Column(Integer, primary_key=True, index=True)
    course = Column(String(100), nullable=False)
    classGroup = Column(String(50), nullable=False, unique=True, index=True) 
    subject = Column(String(100), nullable=False) 

    users = relationship(
        "User",
        secondary=academic_group_user_association, 
        back_populates="groups"
    )

class Post(Base):
    __tablename__ = "Post"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)

    authorId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)

    author = relationship("User", back_populates="posts")
