# ---------------- SCHEMAS (MODELOS DE DADOS) Pydantic ---------------- #
"""
Este arquivo, schemas.py, define os modelos de dados (schemas) da API
utilizando a biblioteca Pydantic.

Esses schemas são cruciais para:
1.  **Validação de Dados:** Garantir que os dados recebidos nas requisições
    (corpo de um POST ou PUT) tenham o formato e os tipos corretos.
2.  **Serialização de Respostas:** Formatar os dados enviados nas respostas
    da API, controlando quais campos são expostos ao cliente.
3.  **Documentação Automática:** Fornecer a estrutura de dados para as
    ferramentas de documentação interativa do FastAPI (Swagger/ReDoc).

Eles desacoplam a lógica da API dos modelos do banco de dados (models.py),
permitindo mais flexibilidade e segurança.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, date, time
from typing import Optional, List
from .models import UserRole, AccessStatus

# --- Schemas de Autenticação ---
# Modelos para o fluxo de login e validação de tokens.
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

class TokenData(BaseModel):
    registration: Optional[str] = None

class UserLogin(BaseModel):
    registration: str
    password: str

# --- Schemas de Usuário ---
# Define as diferentes "visões" dos dados de um usuário: base, criação
# (com senha), resposta (sem senha) e atualização (campos opcionais).
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

# --- Schemas de Eventos (Calendário) ---
# Modelos para criar, atualizar e responder com dados de eventos. Note a
# adaptação de campos como `hora` (para entrada de dados) e a conversão de
# `time` para `str` (para saída em JSON).
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    eventDate: date
    startTime: Optional[time] = None
    endTime: Optional[time] = None
    academicGroupId: Optional[str] = None

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
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    academicGroupId: Optional[str] = None
    creatorId: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Grupos Acadêmicos ---
# Modelos para as operações CRUD de grupos. `AcademicGroupDetailResponse`
# inclui a lista de usuários, demonstrando a composição de schemas.
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

# --- Schemas de Publicações (Posts) ---
# Modelos para as publicações, utilizando `Field` para adicionar validações
# extras, como o comprimento mínimo dos textos.
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

# Em schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Esquemas para Mensagens ---
class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime
    authorId: int

    class Config:
        from_attributes = True

# --- Esquemas para Conversas (Chat) ---
class UserSimple(BaseModel): # Schema simples para não expor dados sensíveis do usuário
    id: int
    name: str

    class Config:
        from_attributes = True
        
class Chat(BaseModel):
    id: int
    participants: List[UserSimple]
    last_message: Optional[Message] = None # Para mostrar a última mensagem na lista de chats

    class Config:
        from_attributes = True

class ChatCreate(BaseModel):
    participant_ids: List[int] # Lista de IDs dos usuários para iniciar a conversa