from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Supondo que estes enums/modelos venham de um arquivo models.py
# from .models import UserRole, AccessStatus

# Exemplo de definições para o código funcionar de forma independente
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    user = "user"

class AccessStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"


# ==============================================================================
# Seção de Autenticação
# ==============================================================================

class Token(BaseModel):
    """
    Schema para o token de acesso JWT.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schema para os dados contidos dentro do token JWT.
    """
    registration: Optional[str] = None


# ==============================================================================
# Seção de Usuário
# ==============================================================================

class UserBase(BaseModel):
    """
    Schema base com os campos comuns de um usuário.
    """
    registration: str
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    """
    Schema para a criação de um novo usuário. Inclui a senha.
    """
    password: str

class UserLogin(BaseModel):
    """
    Schema para o login de um usuário.
    """
    registration: str
    password: str

class UserUpdate(BaseModel):
    """
    Schema para atualização parcial dos dados de um usuário.
    Todos os campos são opcionais.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    accessStatus: Optional[AccessStatus] = None

    class Config:
        # Permite popular o modelo usando nomes de campo alternativos (aliases)
        populate_by_name = True

class UserResponse(UserBase):
    """
    Schema para a resposta da API ao retornar dados de um usuário.
    Não inclui dados sensíveis como a senha.
    """
    id: int
    accessStatus: AccessStatus
    createdAt: datetime

    class Config:
        # Permite que o Pydantic crie o schema a partir de um modelo ORM
        from_attributes = True
        populate_by_name = True


# ==============================================================================
# Seção de Calendário
# ==============================================================================

class EventBase(BaseModel):
    """
    Schema base com os campos comuns de um evento.
    """
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    type: str

class EventCreate(EventBase):
    """
    Schema para a criação de um novo evento. Herda todos os campos de EventBase.
    """
    pass

class EventUpdate(BaseModel):
    """
    Schema para atualização parcial de um evento.
    Todos os campos são opcionais para permitir updates via PATCH.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: Optional[str] = None

class EventResponse(EventBase):
    """
    Schema para a resposta da API ao retornar dados de um evento.
    """
    id: int
    creator_id: int
    created_at: datetime

    class Config:
        # Permite que o Pydantic crie o schema a partir de um modelo ORM
        from_attributes = True
        populate_by_name = True