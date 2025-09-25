# ---------------- AUTHENTICATION SCHEMAS ---------------- #
# Esquemas Pydantic para lidar com a lógica de autenticação, definindo a estrutura dos dados do token e as informações necessárias para o login do usuário.
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from .models import UserRole, AccessStatus 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenData(BaseModel):
    registration: Optional[str] = None

class UserLogin(BaseModel):
    registration: str
    password: str

# ---------------- USER SCHEMAS ---------------- #
# Define as diferentes "formas" de um usuário no sistema: UserBase com os campos comuns, UserCreate para o registro (incluindo senha), UserUpdate para alterações e UserResponse para exibir os dados de um usuário sem expor a senha.

class UserBase(BaseModel):
    registration: str
    name: str
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    accessStatus: AccessStatus
    createdAt: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    accessStatus: Optional[AccessStatus] = None

# ---------------- CALENDAR SCHEMAS ---------------- #
# Esquemas para a criação e visualização de eventos. 

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    classGroup: Optional[str] = None
    event_type: Optional[str] = "evento-geral"

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    classGroup: Optional[str] = None
    event_type: Optional[str] = None

class EventResponse(EventBase):
    id: int
    creatorId: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)