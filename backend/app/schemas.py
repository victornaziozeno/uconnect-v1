from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, date, time
from typing import Optional, List
from .models import UserRole, AccessStatus 

# ---------------- AUTHENTICATION SCHEMAS ---------------- #
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

class UserStatusUpdate(BaseModel):
    accessStatus: AccessStatus

class UserRoleUpdate(BaseModel):
    role: str

# ---------------- CALENDAR SCHEMAS ---------------- #
from datetime import time

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    eventDate: date
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    academicGroupId: Optional[str] = None

class EventCreate(BaseModel):
    title: str
    date: date  # Mantém compatibilidade com frontend
    hora: Optional[str] = None  # Formato: "HH:MM" ou "HH:MM - HH:MM"
    description: Optional[str] = None
    local: Optional[str] = None
    academicGroupId: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    eventDate: Optional[date] = None
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    academicGroupId: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    timestamp: datetime
    eventDate: date
    startTime: Optional[str] = None  # Mudado para string
    endTime: Optional[str] = None    # Mudado para string
    academicGroupId: Optional[str] = None
    creatorId: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# ---------------- GROUP SCHEMAS ---------------- #
class AcademicGroupBase(BaseModel):
    course: str
    classGroup: str
    subject: str

class AcademicGroupCreate(AcademicGroupBase):
    pass

class AcademicGroupUpdate(AcademicGroupBase):
    pass

class AcademicGroupResponse(AcademicGroupBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class AcademicGroupDetailResponse(AcademicGroupResponse):
    users: List[UserResponse] = []

# ---------------- PUBLICATION (POST) SCHEMAS ---------------- #

class PostBase(BaseModel):
    title: str = Field(..., min_length=3)
    content: str = Field(..., min_length=3)

class PostCreate(PostBase):
    pass 

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3)
    content: Optional[str] = Field(None, min_length=3)

class PostResponse(PostBase):
    id: int
    date: datetime
    author: UserResponse
    
    model_config = ConfigDict(from_attributes=True)