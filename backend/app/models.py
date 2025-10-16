# ---------------- MODELOS DO BANCO DE DADOS (SCHEMA) ---------------- #
"""
Este arquivo define todo o schema do banco de dados da aplicação
utilizando o ORM (Object-Relational Mapper) do SQLAlchemy.
"""
from sqlalchemy import (Boolean, Column, Integer, String, DateTime, Date,
                        Enum, ForeignKey, Text, Index, Time, Table)
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .db import Base

# --- ENUMS (Tipos de Dados Personalizados) ---
class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    coordinator = "coordinator"
    admin = "admin"

class AccessStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

class ConversationType(str, enum.Enum):
    direct = "direct"
    group = "group"
    support = "support"

# --- Tabelas de Associação (Muitos-para-Muitos) ---
academic_group_user_association = Table('AcademicGroup_User', Base.metadata,
    Column('groupId', Integer, ForeignKey('AcademicGroup.id'), primary_key=True),
    Column('userId', Integer, ForeignKey('User.id'), primary_key=True)
)

conversation_participants = Table('Conversation_Participants', Base.metadata,
    Column('conversationId', Integer, ForeignKey('Conversation.id'), primary_key=True),
    Column('userId', Integer, ForeignKey('User.id'), primary_key=True),
    Column('joinedAt', DateTime, default=datetime.utcnow, nullable=False)
)

# --- Modelos de Autenticação e Acesso ---
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

    # Relacionamentos
    events_created = relationship("Event", back_populates="creator")
    groups = relationship("AcademicGroup", secondary=academic_group_user_association, back_populates="users")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    
    # Relacionamentos de Chat
    conversations = relationship("Conversation", secondary=conversation_participants, back_populates="participants")
    messages_sent = relationship("Message", back_populates="sender")

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

# --- Modelos de Gestão Acadêmica ---
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
    users = relationship("User", secondary=academic_group_user_association, back_populates="groups")

class Post(Base):
    __tablename__ = "Post"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    authorId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    author = relationship("User", back_populates="posts")

# --- Modelos de Chat ---
class Conversation(Base):
    __tablename__ = "Conversation"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    type = Column(Enum(ConversationType), nullable=False, default=ConversationType.direct)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    participants = relationship("User", secondary=conversation_participants, back_populates="conversations")
    channel = relationship("Channel", uselist=False, back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_conversation_type", "type"),
        Index("idx_conversation_updated", "updatedAt"),
    )

class Channel(Base):
    __tablename__ = 'Channel'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    conversationId = Column(Integer, ForeignKey("Conversation.id", ondelete="CASCADE"))

    conversation = relationship("Conversation", back_populates="channel")
    subchannels = relationship("Subchannel", back_populates="parent_channel", cascade="all, delete-orphan")

class Subchannel(Base):
    __tablename__ = 'Subchannel'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parentChannelId = Column(Integer, ForeignKey("Channel.id", ondelete="CASCADE"))

    parent_channel = relationship("Channel", back_populates="subchannels")
    messages = relationship("Message", back_populates="subchannel", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "Message"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    subchannelId = Column(Integer, ForeignKey("Subchannel.id", ondelete="CASCADE"), nullable=False)
    authorId = Column(Integer, ForeignKey("User.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    isRead = Column(Boolean, default=False, nullable=False)
    
    # Relacionamentos
    subchannel = relationship("Subchannel", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent")

    __table_args__ = (
        Index("idx_message_subchannel", "subchannelId"),
        Index("idx_message_timestamp", "timestamp"),
        Index("idx_message_author", "authorId"),
    )

