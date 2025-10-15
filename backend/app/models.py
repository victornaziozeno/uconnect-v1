# ---------------- MODELOS DO BANCO DE DADOS (SCHEMA) ---------------- #
"""
Este arquivo define todo o schema do banco de dados da aplicação
utilizando o ORM (Object-Relational Mapper) do SQLAlchemy.

Cada classe neste arquivo representa uma tabela no banco de dados, e os
atributos da classe são mapeados para as colunas da tabela. O arquivo também
estabelece os relacionamentos entre as tabelas (ex: um usuário pode criar
vários eventos), define tipos de dados customizados com Enums (como papéis
e status de acesso) e configura tabelas de associação para relacionamentos
muitos-para-muitos.
"""
from sqlalchemy import (Boolean, Column, Integer, String, DateTime, Date,
                        Enum, ForeignKey, Text, Index, Time, Table)
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .db import Base

# --- ENUMS (Tipos de Dados Personalizados) ---
# Define classes Enum para garantir que campos como `role` e `accessStatus`
# só possam receber valores pré-definidos, aumentando a integridade dos dados.
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
    direct = "direct"  # Conversa direta entre 2 usuários
    group = "group"    # Conversa em grupo
    support = "support"  # Atendimento/suporte

# --- Tabelas de Associação (Muitos-para-Muitos) ---
# IMPORTANTE: As tabelas de associação devem ser definidas ANTES dos modelos que as usam

# `academic_group_user_association` é uma tabela auxiliar que mapeia o
# relacionamento N-para-N entre Usuários (`User`) e Grupos Acadêmicos
# (`AcademicGroup`), permitindo que um usuário esteja em vários grupos e
# um grupo tenha vários usuários.
academic_group_user_association = Table('AcademicGroup_User', Base.metadata,
    Column('groupId', Integer, ForeignKey('AcademicGroup.id'), primary_key=True),
    Column('userId', Integer, ForeignKey('User.id'), primary_key=True)
)

# Tabela de associação para participantes de conversas
conversation_participants = Table('Conversation_Participants', Base.metadata,
    Column('conversationId', Integer, ForeignKey('Conversation.id'), primary_key=True),
    Column('userId', Integer, ForeignKey('User.id'), primary_key=True),
    Column('joinedAt', DateTime, default=datetime.utcnow, nullable=False)
)

# --- Modelos de Autenticação e Acesso ---

# A classe `User` representa a tabela de usuários. É o modelo central para
# autenticação, armazenando informações como matrícula, e-mail, senha (hash),
# papel e status. Os `relationships` definem como um usuário se conecta a
# outros modelos.
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

    # Relacionamentos existentes
    events_created = relationship("Event", back_populates="creator")
    groups = relationship(
        "AcademicGroup",
        secondary=academic_group_user_association,
        back_populates="users"
    )
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    
    # Relacionamentos de Chat
    conversations = relationship(
        "Conversation",
        secondary=conversation_participants,
        back_populates="participants"
    )
    messages_sent = relationship("Message", back_populates="sender")

    __table_args__ = (
        Index("ix_users_registration", "registration"),
        Index("ix_users_email", "email"),
    )

# A classe `Session` armazena os tokens de sessão gerados para os usuários
# logados, relacionando um token a um ID de usuário e controlando sua expiração.
class Session(Base):
    __tablename__ = "Session"

    token = Column(String(500), primary_key=True, index=True, nullable=False)
    userId = Column(Integer, ForeignKey("User.id"), nullable=False, index=True)
    startDate = Column(DateTime, default=datetime.utcnow, nullable=False)
    expirationDate = Column(DateTime, nullable=False)

    user = relationship("User", lazy="joined")

# --- Modelos de Gestão Acadêmica ---

# Representa a tabela de eventos. Armazena detalhes sobre cada evento, como
# título, data, hora e o criador, com uma chave estrangeira para o modelo `User`.
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

# Define um grupo acadêmico, geralmente representando uma turma de um curso e
# disciplina específicos.
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

# Representa as publicações (posts) feitas por usuários. Contém o conteúdo do
# post e uma chave estrangeira que o vincula ao seu autor (`User`).
# O `ondelete="CASCADE"` garante que os posts de um usuário sejam deletados
# caso o próprio usuário seja removido.
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
    title = Column(String(200), nullable=True)  # Título da conversa (para grupos)
    type = Column(Enum(ConversationType), nullable=False, default=ConversationType.direct)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    participants = relationship(
        "User",
        secondary=conversation_participants,
        back_populates="conversations"
    )
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_conversation_type", "type"),
        Index("idx_conversation_updated", "updatedAt"),
    )

class Message(Base):
    __tablename__ = "Message"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    conversationId = Column(Integer, ForeignKey("Conversation.id", ondelete="CASCADE"), nullable=False)
    senderId = Column(Integer, ForeignKey("User.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    isRead = Column(Boolean, default=False, nullable=False)
    
    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent")
    
    __table_args__ = (
        Index("idx_message_conversation", "conversationId"),
        Index("idx_message_timestamp", "timestamp"),
        Index("idx_message_sender", "senderId"),
    )