# ---------------- AUTHENTICATION SCHEMAS ---------------- #
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from datetime import date
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
    
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    accessStatus: Optional[AccessStatus] = None

# ---------------- CALENDAR SCHEMAS ---------------- #
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    timestamp: datetime
    academicGroupId: Optional[str] = None
    #eventType: Optional[str] = "evento-geral"

class EventCreate(BaseModel):
    title: str
    date: date
    hora: Optional[str] = None
    description: Optional[str] = None
    local: Optional[str] = None
    academicGroupId: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    academicGroupId: Optional[str] = None
    #eventType: Optional[str] = None

class EventResponse(EventBase):
    id: int
    creatorId: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
