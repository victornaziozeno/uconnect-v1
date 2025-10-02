# ---------------- CONFIGURATION & CONTEXT ---------------- #
# Esta seção agora fica mais limpa, importando as configurações e definindo apenas o que é específico deste arquivo.

from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .db import get_db
from . import models
from .config import settings  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------- UTILITY FUNCTIONS ---------------- #
# As funções de senha e criação de token continuam aqui, mas agora usam as configurações importadas.
def decode_token(token: str) -> dict | None:
    """
    Decodifica um token JWT e retorna o payload.
    Retorna None se o token for inválido.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_minutes: int = None) -> tuple[str, datetime]:
    to_encode = data.copy()
    if expires_minutes:
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # Usa config
    
    to_encode.update({"exp": expire, "sub": data.get("sub")})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM) # type: ignore # Usa config
    return encoded_jwt, expire

# ---------------- CORE DEPENDENCIES ---------------- #
# A função get_current_user fica muito mais limpa e focada.

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar as credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
        
    registration: str = payload.get("sub")
    if registration is None:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.registration == registration).first()
    if user is None:
        raise credentials_exception
    
    if user.accessStatus != models.AccessStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso inativo")

    session = db.query(models.Session).filter(models.Session.token == token).first()
    if session is None or session.expirationDate < datetime.utcnow():
        if session:
            db.delete(session)
            db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida ou expirada")

    return user

# ---------------- AUTHORIZATION FACTORY ---------------- #
# As funções de autorização não mudam, pois dependem de get_current_user.

async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    # Esta verificação já está em get_current_user, mas pode ser mantida por segurança extra.
    if current_user.accessStatus != models.AccessStatus.active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user

def require_roles(allowed_roles: list[str]):
    async def role_checker(current_user: models.User = Depends(get_current_active_user)):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada")
        return current_user
    return role_checker
