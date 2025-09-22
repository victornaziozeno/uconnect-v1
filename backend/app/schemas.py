from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Union
from .models import UserRole, AccessStatus  

class Config:
        from_attributes = True
        populate_by_name = True
        orm_mode = True
        populate_by_name = True

// Autenticação
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    registration: Optional[str] = None

class UserBase(BaseModel):
    registration: str
    name: str
    email: EmailStr
    role: UserRole  

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    registration: str
    password: str

class UserResponse(UserBase):
    id: int
    passwordHash: str
    accessStatus: AccessStatus 
    createdAt: datetime 

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    accessStatus: Optional[AccessStatus] = None  

// Calendário
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    type: str

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    creator_id: int
    created_at: datetime
    

