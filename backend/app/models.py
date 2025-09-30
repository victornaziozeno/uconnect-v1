from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from .db import Base

# ---------------- ENUMS ---------------- #
# Esta seção define os Enums do Python para padronizar os valores permitidos para papéis de usuário (UserRole) e status de acesso (AccessStatus), garantindo a consistência dos dados.

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

class AccessStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"

# ---------------- AUTHENTICATION & ACCESS ---------------- #
# Este bloco contém os modelos para User (Usuário) e Session (Sessão), que são a base para o pacote de autenticação e controle de acesso da aplicação.

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

# ---------------- ACADEMIC MANAGEMENT ---------------- #
# A seguir, o modelo para Event (Evento), que faz parte do pacote de Gestão Acadêmica e será usado para popular o calendário.


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    classGroup = Column(String(50), nullable=True)
    creatorId = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), default="evento-geral")
    
    creator = relationship("User", back_populates="events_created")
    
    __table_args__ = (
        Index("idx_event_start", "start_time"),
        Index("idx_event_creator", "creatorId"),
    )